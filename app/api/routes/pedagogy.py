from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.pedagogy import (
    MistakeIn,
    MistakeOut,
    PedagogyDashboardOut,
    PlacementIn,
    PlacementOut,
    RecommendationOut,
    ReviewQueueItemOut,
    VocabularyReviewIn,
)
from app.services.adaptive_learning_service import (
    bootstrap_initial_vocab_progress,
    build_recommendations,
    build_track_progress,
    get_or_create_learner_profile,
    list_review_queue,
    log_mistake,
    recurring_errors,
    review_vocabulary,
    run_placement,
    select_next_step,
    strengths_list,
    weaknesses_list,
    words_in_review_count,
)
from app.services.analytics_service import track_event
from app.services.pedagogy_seed import ensure_pedagogical_seed

router = APIRouter(prefix="/pedagogy", tags=["pedagogy"])


@router.post("/placement", response_model=PlacementOut)
def placement_assessment(
    payload: PlacementIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    profile = run_placement(db, user, payload.model_dump())
    track_event(db, "placement_completed", user_id=user.id, payload={"level": profile.estimated_level})
    db.commit()
    return PlacementOut(
        estimated_level=profile.estimated_level,
        confidence=profile.level_confidence,
        speaking_score=profile.speaking_score,
        vocabulary_score=profile.vocabulary_score,
        grammar_score=profile.grammar_score,
        fluency_score=profile.fluency_score,
    )


@router.post("/mistakes", response_model=MistakeOut)
def register_mistake(
    payload: MistakeIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    mistake = log_mistake(
        db,
        user_id=user.id,
        error_type=payload.error_type,
        user_text=payload.user_text,
        corrected_text=payload.corrected_text,
        explanation=payload.explanation,
        severity=payload.severity,
        context_feature=payload.context_feature,
    )
    track_event(db, "weakness_detected", user_id=user.id, payload={"error_type": payload.error_type})
    db.commit()
    return MistakeOut(id=mistake.id, error_type=mistake.error_type, severity=mistake.severity, explanation=mistake.explanation)


@router.post("/vocabulary/review")
def vocabulary_review(
    payload: VocabularyReviewIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    progress = review_vocabulary(db, user.id, payload.item_id, payload.correct)
    track_event(
        db,
        "review_completed",
        user_id=user.id,
        payload={"item_id": payload.item_id, "correct": payload.correct, "status": progress.status},
    )
    if progress.status == "mastered":
        track_event(db, "vocabulary_mastered", user_id=user.id, payload={"item_id": payload.item_id})
    db.commit()
    return {
        "item_id": payload.item_id,
        "status": progress.status,
        "next_review_at": progress.next_review_at.isoformat(),
        "correct_count": progress.correct_count,
        "wrong_count": progress.wrong_count,
    }


@router.get("/recommendations", response_model=list[RecommendationOut])
def recommendations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    profile = get_or_create_learner_profile(db, user.id)
    bootstrap_initial_vocab_progress(db, user.id)
    recs = build_recommendations(db, user, profile)
    track_event(db, "adaptive_recommendation_clicked", user_id=user.id, payload={"count": len(recs)})
    db.commit()
    return [RecommendationOut(**item) for item in recs]


@router.get("/review-queue", response_model=list[ReviewQueueItemOut])
def review_queue(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    bootstrap_initial_vocab_progress(db, user.id)
    rows = list_review_queue(db, user.id)
    return [
        ReviewQueueItemOut(
            id=item.id,
            queue_type=item.queue_type,
            reference_id=item.reference_id,
            due_at=item.due_at,
            priority=item.priority,
        )
        for item in rows
    ]


@router.get("/dashboard", response_model=PedagogyDashboardOut)
def pedagogy_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    profile = get_or_create_learner_profile(db, user.id)
    bootstrap_initial_vocab_progress(db, user.id)

    recommendations_data = build_recommendations(db, user, profile)
    next_step_data = select_next_step(db, user, profile)

    return PedagogyDashboardOut(
        estimated_level=profile.estimated_level,
        confidence=profile.level_confidence,
        strengths=strengths_list(db, user.id),
        weaknesses=weaknesses_list(db, user.id),
        recurring_errors=recurring_errors(db, user.id),
        words_in_review=words_in_review_count(db, user.id),
        next_step=RecommendationOut(**next_step_data),
        track_progress=build_track_progress(db),
        recommendations=[RecommendationOut(**item) for item in recommendations_data],
    )
