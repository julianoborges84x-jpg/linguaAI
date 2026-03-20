from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.pedagogy import (
    ClickAdvanceIn,
    ClickAdvanceOut,
    ClickLessonOut,
    ClickPathUnitOut,
    CurrentTrackOut,
    LessonDetailOut,
    LessonSubmitIn,
    LessonSubmitOut,
    LessonStepSaveIn,
    LessonStepSaveOut,
    MistakeIn,
    MistakeOut,
    ModuleOut,
    PedagogyDashboardOut,
    PlacementIn,
    PlacementOut,
    RecommendationOut,
    ProgressSummaryOut,
    ReviewSubmitIn,
    ReviewSubmitOut,
    ReviewTodayOut,
    ReviewQueueItemOut,
    VocabularyReviewIn,
)
from app.services.adaptive_learning_service import (
    advance_click_step,
    build_click_lesson,
    bootstrap_initial_vocab_progress,
    build_recommendations,
    build_track_progress,
    get_or_create_learner_profile,
    get_or_create_unit_progress,
    list_click_path_units,
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
from app.services.learning_journey_service import (
    get_current_track,
    get_lesson_detail,
    get_module_detail,
    get_modules,
    get_review_today,
    progress_summary,
    save_lesson_step,
    submit_lesson,
    submit_review_item,
)

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
        track_progress=build_track_progress(db, user),
        recommendations=[RecommendationOut(**item) for item in recommendations_data],
    )


@router.get("/click-path", response_model=list[ClickPathUnitOut])
def click_path(
    level: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    units = list_click_path_units(db, user, level=level, limit=24)
    output: list[ClickPathUnitOut] = []
    for unit in units:
        progress = get_or_create_unit_progress(db, user.id, unit.id)
        output.append(
            ClickPathUnitOut(
                unit_id=unit.id,
                title=unit.title,
                cefr_level=unit.cefr_level,
                primary_skill=unit.primary_skill,
                is_pro_only=unit.is_pro_only,
                completed=progress.completed,
                current_step=progress.current_step,
                total_steps=progress.total_steps,
            )
        )
    db.commit()
    return output


@router.get("/units/{unit_id}/click-lesson", response_model=ClickLessonOut)
def click_lesson(
    unit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    payload = build_click_lesson(db, user, unit_id)
    if not payload:
        return ClickLessonOut(
            unit_id=unit_id,
            title="Unit not found",
            description="This lesson is not available for your target language.",
            cefr_level="A1",
            language_code="en",
            current_step=0,
            total_steps=0,
            completed=False,
            score=0.0,
            steps=[],
        )
    db.commit()
    return ClickLessonOut(**payload)


@router.post("/units/{unit_id}/click-lesson/advance", response_model=ClickAdvanceOut)
def click_lesson_advance(
    unit_id: int,
    payload: ClickAdvanceIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    result = advance_click_step(db, user, unit_id, correct=payload.correct, score_delta=payload.score_delta)
    if not result:
        return ClickAdvanceOut(unit_id=unit_id, current_step=0, total_steps=0, completed=False, score=0.0)
    db.commit()
    return ClickAdvanceOut(**result)


@router.get("/track/current", response_model=CurrentTrackOut)
def track_current(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    payload = get_current_track(db, user)
    db.commit()
    return CurrentTrackOut(**payload)


@router.get("/modules", response_model=list[ModuleOut])
def modules(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    payload = get_modules(db, user)
    db.commit()
    return [ModuleOut(**item) for item in payload]


@router.get("/modules/{module_id}", response_model=ModuleOut)
def module_detail(
    module_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    payload = get_module_detail(db, user, module_id)
    if not payload:
        return ModuleOut(id=module_id, slug="not-found", title="Modulo nao encontrado", progress_percent=0, lessons=[])
    db.commit()
    return ModuleOut(**payload)


@router.get("/lessons/{lesson_id}", response_model=LessonDetailOut)
def lesson_detail(
    lesson_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    payload = get_lesson_detail(db, user, lesson_id)
    if not payload:
        return LessonDetailOut(
            id=lesson_id,
            module_name="Indefinido",
            order_index=0,
            title="Licao nao encontrada",
            lesson_objective="",
            cefr_level="A1",
            estimated_duration_min=0,
            target_vocabulary=[],
            key_structures=[],
            grammar_explanation_pt="",
            examples=[],
            exercises=[],
            ai_context={},
            final_review=[],
            completion_criteria={"min_exercises_correct": 0, "min_conversation_turns": 0, "checkpoint_required": False},
            progress={"current_step": 0, "total_steps": 0, "completed": False, "score": 0.0},
        )
    db.commit()
    return LessonDetailOut(**payload)


@router.post("/lessons/{lesson_id}/submit", response_model=LessonSubmitOut)
def lesson_submit(
    lesson_id: int,
    payload: LessonSubmitIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    result = submit_lesson(
        db,
        user,
        lesson_id=lesson_id,
        correct_count=payload.correct_count,
        total_count=payload.total_count,
        conversation_turns=payload.conversation_turns,
    )
    if not result:
        return LessonSubmitOut(lesson_id=lesson_id, completed=False, accuracy=0.0, next_review_at="", next_step="not_found")
    db.commit()
    return LessonSubmitOut(**result)


@router.post("/lessons/{lesson_id}/step", response_model=LessonStepSaveOut)
def lesson_step_save(
    lesson_id: int,
    payload: LessonStepSaveIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    result = save_lesson_step(db, user, lesson_id, payload.current_step)
    if not result:
        return LessonStepSaveOut(lesson_id=lesson_id, current_step=0, total_steps=10, completed=False, score=0.0)
    db.commit()
    return LessonStepSaveOut(**result)


@router.get("/review/today", response_model=ReviewTodayOut)
def review_today(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    payload = get_review_today(db, user)
    return ReviewTodayOut(**payload)


@router.post("/review/submit", response_model=ReviewSubmitOut)
def review_submit(
    payload: ReviewSubmitIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    result = submit_review_item(db, user, payload.review_item_id, payload.correct)
    if not result:
        return ReviewSubmitOut(review_item_id=payload.review_item_id, correct=payload.correct, next_review_at="")
    db.commit()
    return ReviewSubmitOut(**result)


@router.get("/progress/summary", response_model=ProgressSummaryOut)
def summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ensure_pedagogical_seed(db)
    payload = progress_summary(db, user)
    return ProgressSummaryOut(**payload)
