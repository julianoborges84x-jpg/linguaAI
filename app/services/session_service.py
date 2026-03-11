from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.study_session import StudySession
from app.models.user import User
from app.services.progress_service import mark_daily_activity, recalculate_level, today_for_user

ALLOWED_MODES = {"chat", "vocab", "speaking", "writing"}


def _compute_xp(started_at: datetime, finished_at: datetime, interactions_count: int) -> int:
    duration_minutes = max(1, int((finished_at - started_at).total_seconds() // 60))
    return max(1, duration_minutes * 2 + max(0, interactions_count) * 3)


def start_session(db: Session, user: User, mode: str, topic_id: int | None = None) -> StudySession:
    normalized_mode = mode.strip().lower()
    if normalized_mode not in ALLOWED_MODES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid session mode",
        )

    session = StudySession(
        user_id=user.id,
        mode=normalized_mode,
        topic_id=topic_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def finish_session(db: Session, user: User, session_id: int, interactions_count: int | None = None) -> StudySession:
    session = (
        db.query(StudySession)
        .filter(StudySession.id == session_id, StudySession.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.finished_at is not None:
        return session

    if interactions_count is not None:
        session.interactions_count = max(0, interactions_count)

    session.finished_at = datetime.utcnow()
    session.xp_earned = _compute_xp(session.started_at, session.finished_at, session.interactions_count)

    user.xp_total = max(0, (user.xp_total or 0) + session.xp_earned)
    user.level = recalculate_level(user.xp_total)

    mark_daily_activity(db, user.id, today_for_user(user))
    db.commit()
    db.refresh(session)
    return session
