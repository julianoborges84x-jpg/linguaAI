from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.study_session import StudySession
from app.models.user import User
from app.services.analytics_service import track_event
from app.services.growth_service import progress_mission_on_session_finish, update_streak
from app.services.progress_service import mark_daily_activity, recalculate_level, today_for_user
from app.services.topic_service import get_first_topic_id, topic_exists

ALLOWED_MODES = {"chat", "vocab", "speaking", "writing"}
MODE_ALIASES = {"lesson": "writing"}


def _compute_xp(started_at: datetime, finished_at: datetime, interactions_count: int) -> int:
    duration_minutes = max(1, int((finished_at - started_at).total_seconds() // 60))
    return max(1, duration_minutes * 2 + max(0, interactions_count) * 3)


def start_session(db: Session, user: User, mode: str, topic_id: int | None = None) -> StudySession:
    normalized_mode = MODE_ALIASES.get(mode.strip().lower(), mode.strip().lower())
    if normalized_mode not in ALLOWED_MODES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid session mode",
        )

    final_topic_id: int | None
    if topic_id is None or topic_id <= 0:
        final_topic_id = get_first_topic_id(db)
    else:
        if not topic_exists(db, topic_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Invalid topic_id",
            )
        final_topic_id = topic_id

    session = StudySession(
        user_id=user.id,
        mode=normalized_mode,
        topic_id=final_topic_id,
    )
    db.add(session)
    track_event(
        db,
        "lesson_started",
        user_id=user.id,
        payload={"mode": normalized_mode, "topic_id": final_topic_id},
    )
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

    session.finished_at = datetime.now(UTC).replace(tzinfo=None)
    session.xp_earned = _compute_xp(session.started_at, session.finished_at, session.interactions_count)

    user.xp_total = max(0, (user.xp_total or 0) + session.xp_earned)
    user.level = recalculate_level(user.xp_total)

    active_day = today_for_user(user)
    mark_daily_activity(db, user.id, active_day)
    update_streak(user, active_day)
    mission = progress_mission_on_session_finish(db, user, active_day)
    track_event(
        db,
        "lesson_completed",
        user_id=user.id,
        payload={
            "session_id": session.id,
            "xp_earned": session.xp_earned,
            "current_streak": user.current_streak,
            "mission_completed": mission.completed_sessions >= mission.target_sessions,
        },
    )
    track_event(
        db,
        "streak_updated",
        user_id=user.id,
        payload={"current_streak": user.current_streak, "longest_streak": user.longest_streak},
    )
    db.commit()
    db.refresh(session)
    return session
