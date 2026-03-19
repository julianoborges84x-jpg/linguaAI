from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import PlanEnum, User
from app.models.pedagogy import (
    LearnerProfile,
    LearnerStrength,
    LearnerWeakness,
    LearningTrack,
    LearningUnit,
    MistakeLog,
    ReviewQueue,
    VocabularyItem,
    VocabularyProgress,
)

LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1"]


def _score_to_level(score: float) -> str:
    if score < 0.22:
        return "A1"
    if score < 0.4:
        return "A2"
    if score < 0.58:
        return "B1"
    if score < 0.78:
        return "B2"
    return "C1"


def get_or_create_learner_profile(db: Session, user_id: int) -> LearnerProfile:
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()
    if profile:
        return profile

    profile = LearnerProfile(user_id=user_id)
    db.add(profile)
    db.flush()
    return profile


def run_placement(db: Session, user: User, metrics: dict[str, float]) -> LearnerProfile:
    profile = get_or_create_learner_profile(db, user.id)

    sentence_complexity = max(0.0, min(1.0, float(metrics.get("sentence_complexity", 0.0))))
    vocabulary_variety = max(0.0, min(1.0, float(metrics.get("vocabulary_variety", 0.0))))
    error_frequency = max(0.0, min(1.0, float(metrics.get("error_frequency", 0.0))))
    tense_control = max(0.0, min(1.0, float(metrics.get("tense_control", 0.0))))
    autonomy = max(0.0, min(1.0, float(metrics.get("autonomy", 0.0))))
    clarity = max(0.0, min(1.0, float(metrics.get("clarity", 0.0))))

    grammar_score = max(0.0, min(1.0, (tense_control + (1.0 - error_frequency)) / 2.0))
    vocabulary_score = vocabulary_variety
    speaking_score = (autonomy + clarity) / 2.0
    fluency_score = (sentence_complexity + clarity + autonomy) / 3.0
    confidence = max(0.2, min(0.98, (sentence_complexity + vocabulary_variety + tense_control + autonomy + clarity) / 5.0))

    overall = (grammar_score + vocabulary_score + speaking_score + fluency_score) / 4.0
    profile.estimated_level = _score_to_level(overall)
    profile.level_confidence = confidence
    profile.grammar_score = grammar_score
    profile.vocabulary_score = vocabulary_score
    profile.speaking_score = speaking_score
    profile.fluency_score = fluency_score
    profile.listening_score = (clarity + 0.4) / 1.4
    profile.updated_at = datetime.utcnow()

    db.add(profile)
    return profile


def log_mistake(
    db: Session,
    user_id: int,
    error_type: str,
    user_text: str,
    corrected_text: str,
    explanation: str,
    severity: int,
    context_feature: str,
) -> MistakeLog:
    row = MistakeLog(
        user_id=user_id,
        error_type=error_type.strip().lower(),
        user_text=user_text,
        corrected_text=corrected_text,
        explanation=explanation,
        severity=max(1, min(5, severity)),
        context_feature=context_feature,
    )
    db.add(row)
    db.flush()

    weakness = (
        db.query(LearnerWeakness)
        .filter(LearnerWeakness.user_id == user_id, LearnerWeakness.skill_tag == row.error_type)
        .first()
    )
    if not weakness:
        weakness = LearnerWeakness(user_id=user_id, skill_tag=row.error_type, severity=min(1.0, row.severity / 5.0), occurrences=1)
    else:
        weakness.occurrences += 1
        weakness.severity = min(1.0, weakness.severity + (row.severity / 25.0))
        weakness.last_seen_at = datetime.utcnow()
    db.add(weakness)

    queue = ReviewQueue(
        user_id=user_id,
        queue_type="mistake_reinforcement",
        reference_id=row.id,
        priority=min(5, row.severity),
        due_at=datetime.utcnow() + timedelta(hours=12),
        status="pending",
    )
    db.add(queue)
    return row


def update_strength(db: Session, user_id: int, skill_tag: str, boost: float = 0.08) -> None:
    row = db.query(LearnerStrength).filter(LearnerStrength.user_id == user_id, LearnerStrength.skill_tag == skill_tag).first()
    if not row:
        row = LearnerStrength(user_id=user_id, skill_tag=skill_tag, score=max(0.1, boost), evidence_count=1)
    else:
        row.score = min(1.0, row.score + boost)
        row.evidence_count += 1
        row.updated_at = datetime.utcnow()
    db.add(row)


def ensure_user_vocab_progress(db: Session, user_id: int, item_id: int) -> VocabularyProgress:
    row = db.query(VocabularyProgress).filter(VocabularyProgress.user_id == user_id, VocabularyProgress.item_id == item_id).first()
    if row:
        return row
    row = VocabularyProgress(user_id=user_id, item_id=item_id)
    db.add(row)
    db.flush()
    return row


def review_vocabulary(db: Session, user_id: int, item_id: int, correct: bool) -> VocabularyProgress:
    progress = ensure_user_vocab_progress(db, user_id, item_id)
    now = datetime.utcnow()

    if correct:
        progress.correct_count += 1
        progress.interval_days = min(21, max(1, progress.interval_days * 2))
        progress.ease_factor = min(3.0, progress.ease_factor + 0.05)
        if progress.correct_count >= 4:
            progress.status = "mastered"
        elif progress.correct_count >= 2:
            progress.status = "review"
        else:
            progress.status = "learning"
    else:
        progress.wrong_count += 1
        progress.interval_days = 1
        progress.ease_factor = max(1.3, progress.ease_factor - 0.2)
        progress.status = "learning"

    progress.next_review_at = now + timedelta(days=progress.interval_days)
    progress.last_seen_at = now
    db.add(progress)

    queue = ReviewQueue(
        user_id=user_id,
        queue_type="vocabulary",
        reference_id=item_id,
        priority=1 if correct else 4,
        due_at=progress.next_review_at,
        status="pending",
    )
    db.add(queue)
    return progress


def build_recommendations(db: Session, user: User, profile: LearnerProfile) -> list[dict[str, object]]:
    top_weaknesses = (
        db.query(LearnerWeakness)
        .filter(LearnerWeakness.user_id == user.id)
        .order_by(LearnerWeakness.severity.desc(), LearnerWeakness.occurrences.desc())
        .limit(3)
        .all()
    )

    due_vocab = (
        db.query(VocabularyProgress)
        .filter(VocabularyProgress.user_id == user.id, VocabularyProgress.next_review_at <= datetime.utcnow())
        .count()
    )

    recs: list[dict[str, object]] = []
    if top_weaknesses:
        weak = top_weaknesses[0]
        recs.append(
            {
                "recommendation_type": "weakness_focus",
                "title": f"Reforcar {weak.skill_tag}",
                "description": "Pratica contextual para reduzir seu erro mais recorrente.",
                "locked_for_free": False,
            }
        )

    if due_vocab > 0:
        recs.append(
            {
                "recommendation_type": "vocabulary_review",
                "title": "Revisar vocabulario",
                "description": f"Voce tem {due_vocab} palavras em revisao.",
                "locked_for_free": False,
            }
        )

    next_unit = db.query(LearningUnit).filter(LearningUnit.cefr_level == profile.estimated_level).order_by(LearningUnit.id.asc()).first()
    if next_unit:
        locked = bool(next_unit.is_pro_only and user.plan == PlanEnum.FREE)
        recs.append(
            {
                "recommendation_type": "continue_track",
                "title": next_unit.title,
                "description": next_unit.learning_objective,
                "locked_for_free": locked,
            }
        )

    if not recs:
        recs.append(
            {
                "recommendation_type": "speaking_practice",
                "title": "Falar com mentor",
                "description": "Mantenha ritmo com uma pratica curta de speaking.",
                "locked_for_free": False,
            }
        )
    return recs


def build_track_progress(db: Session) -> list[dict[str, object]]:
    rows = (
        db.query(LearningUnit.cefr_level, func.count(LearningUnit.id))
        .group_by(LearningUnit.cefr_level)
        .order_by(LearningUnit.cefr_level.asc())
        .all()
    )
    progress = []
    for level, total in rows:
        progress.append({"level": level, "completed_units": 0, "total_units": int(total)})
    return progress


def select_next_step(db: Session, user: User, profile: LearnerProfile) -> dict[str, object]:
    recs = build_recommendations(db, user, profile)
    return recs[0]


def list_review_queue(db: Session, user_id: int) -> list[ReviewQueue]:
    return (
        db.query(ReviewQueue)
        .filter(ReviewQueue.user_id == user_id, ReviewQueue.status == "pending")
        .order_by(ReviewQueue.due_at.asc(), ReviewQueue.priority.desc())
        .limit(20)
        .all()
    )


def recurring_errors(db: Session, user_id: int) -> list[str]:
    rows = (
        db.query(MistakeLog.error_type, func.count(MistakeLog.id).label("cnt"))
        .filter(MistakeLog.user_id == user_id)
        .group_by(MistakeLog.error_type)
        .order_by(func.count(MistakeLog.id).desc())
        .limit(5)
        .all()
    )
    return [f"{row[0]} ({row[1]})" for row in rows]


def words_in_review_count(db: Session, user_id: int) -> int:
    return (
        db.query(VocabularyProgress.id)
        .filter(VocabularyProgress.user_id == user_id, VocabularyProgress.status.in_(["learning", "review"]))
        .count()
    )


def strengths_list(db: Session, user_id: int) -> list[str]:
    rows = (
        db.query(LearnerStrength)
        .filter(LearnerStrength.user_id == user_id)
        .order_by(LearnerStrength.score.desc(), LearnerStrength.evidence_count.desc())
        .limit(4)
        .all()
    )
    return [row.skill_tag for row in rows]


def weaknesses_list(db: Session, user_id: int) -> list[str]:
    rows = (
        db.query(LearnerWeakness)
        .filter(LearnerWeakness.user_id == user_id)
        .order_by(LearnerWeakness.severity.desc(), LearnerWeakness.occurrences.desc())
        .limit(4)
        .all()
    )
    return [row.skill_tag for row in rows]


def bootstrap_initial_vocab_progress(db: Session, user_id: int, limit: int = 4) -> None:
    existing = db.query(VocabularyProgress.id).filter(VocabularyProgress.user_id == user_id).count()
    if existing > 0:
        return
    items = db.query(VocabularyItem).order_by(VocabularyItem.id.asc()).limit(limit).all()
    for item in items:
        ensure_user_vocab_progress(db, user_id, item.id)
