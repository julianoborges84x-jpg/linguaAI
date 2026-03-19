from datetime import date, datetime, timedelta
from math import floor
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.orm import Session

from app.models.daily_activity import DailyActivity
from app.models.daily_message import DailyMessage
from app.models.study_session import StudySession
from app.models.user import User

DEFAULT_TIMEZONE = "America/Sao_Paulo"


def resolve_timezone(user: User) -> ZoneInfo:
    tz_name = (user.timezone or "").strip() or DEFAULT_TIMEZONE
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo(DEFAULT_TIMEZONE)


def now_for_user(user: User) -> datetime:
    return datetime.now(resolve_timezone(user))


def today_for_user(user: User) -> date:
    return now_for_user(user).date()


def mark_daily_activity(db: Session, user_id: int, active_day: date) -> None:
    exists = (
        db.query(DailyActivity.id)
        .filter(DailyActivity.user_id == user_id, DailyActivity.day_date == active_day)
        .first()
    )
    if exists:
        return
    db.add(DailyActivity(user_id=user_id, day_date=active_day))


def calculate_streak(db: Session, user_id: int, current_day: date) -> int:
    activity_days = {
        day
        for (day,) in (
            db.query(DailyActivity.day_date).filter(DailyActivity.user_id == user_id).distinct().all()
        )
    }
    message_days = {
        day
        for (day,) in (
            db.query(DailyMessage.day).filter(DailyMessage.user_id == user_id).distinct().all()
        )
    }
    all_days = activity_days.union(message_days)

    streak = 0
    cursor = current_day
    while cursor in all_days:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak


def calculate_weekly_minutes(db: Session, user_id: int, current_day: date) -> int:
    week_start = datetime.combine(current_day - timedelta(days=6), datetime.min.time())
    sessions = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == user_id,
            StudySession.finished_at.is_not(None),
            StudySession.started_at >= week_start,
        )
        .all()
    )
    total_minutes = 0
    for session in sessions:
        duration = session.finished_at - session.started_at
        minutes = max(1, int(duration.total_seconds() // 60))
        total_minutes += minutes
    return total_minutes


def recalculate_level(xp_total: int) -> int:
    return min(10, floor(max(0, xp_total) / 100))


def build_progress_summary(db: Session, user: User) -> dict[str, int]:
    today = today_for_user(user)
    streak = max(calculate_streak(db, user.id, today), max(0, user.current_streak or 0))
    weekly_minutes = calculate_weekly_minutes(db, user.id, today)
    return {
        "xp_total": max(0, user.xp_total or 0),
        "level": recalculate_level(user.xp_total or 0),
        "streak_days": streak,
        "weekly_minutes": weekly_minutes,
    }
