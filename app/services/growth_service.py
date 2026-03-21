from __future__ import annotations

import secrets
import string
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.daily_mission import DailyMissionProgress
from app.models.study_session import StudySession
from app.models.user import User
from app.services.analytics_service import track_event
from app.services.progress_service import recalculate_level, today_for_user

MISSION_TARGET_SESSIONS = 1
MISSION_BONUS_XP = 25
REFERRAL_BONUS_XP = 150
REFERRAL_PRO_BONUS_DAYS = 1


def _to_base36(value: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if value <= 0:
        return "0"
    out = ""
    cursor = value
    while cursor:
        cursor, rem = divmod(cursor, 36)
        out = digits[rem] + out
    return out


def _generate_referral_code() -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "lingua" + "".join(secrets.choice(alphabet) for _ in range(5))


def ensure_referral_code(db: Session, user: User) -> str:
    if user.referral_code:
        normalized = user.referral_code.strip().lower()
        owner = db.query(User.id).filter(User.referral_code == normalized).first()
        if not owner or int(owner[0]) == int(user.id):
            user.referral_code = normalized
            return user.referral_code

    # Deterministic default avoids race conditions and collisions in concurrent requests.
    deterministic = "lingua" + _to_base36(int(user.id)).rjust(5, "0")[-5:]
    owner = db.query(User.id).filter(User.referral_code == deterministic).first()
    if not owner or int(owner[0]) == int(user.id):
        user.referral_code = deterministic
        return deterministic

    code = _generate_referral_code()
    while db.query(User.id).filter(User.referral_code == code).first():
        code = _generate_referral_code()
    user.referral_code = code
    return code


def apply_referral_if_valid(db: Session, user: User, referral_code: str | None) -> None:
    if not referral_code:
        return

    normalized = referral_code.strip().lower()
    if not normalized:
        return

    referrer = db.query(User).filter(User.referral_code == normalized).first()
    if not referrer:
        return

    if referrer.id == user.id:
        return

    if user.referred_by_user_id is not None:
        return

    user.referred_by_user_id = referrer.id
    referrer.referred_count = max(0, (referrer.referred_count or 0) + 1)
    referrer.xp_total = max(0, (referrer.xp_total or 0) + REFERRAL_BONUS_XP)
    user.xp_total = max(0, (user.xp_total or 0) + REFERRAL_BONUS_XP)
    referrer.level = recalculate_level(referrer.xp_total)
    user.level = recalculate_level(user.xp_total)

    today = today_for_user(user)
    referrer.pro_access_until = max(referrer.pro_access_until or today, today) + timedelta(days=REFERRAL_PRO_BONUS_DAYS)
    user.pro_access_until = max(user.pro_access_until or today, today) + timedelta(days=REFERRAL_PRO_BONUS_DAYS)

    track_event(db, "referral_signup", user_id=user.id, payload={"referrer_id": referrer.id, "referral_code": normalized})
    track_event(
        db,
        "referral_reward_granted",
        user_id=referrer.id,
        payload={"referred_user_id": user.id, "xp_reward": REFERRAL_BONUS_XP, "pro_bonus_days": REFERRAL_PRO_BONUS_DAYS},
    )


def update_streak(user: User, active_day: date) -> None:
    if user.last_active_date == active_day:
        return

    previous_day = active_day - timedelta(days=1)
    if user.last_active_date == previous_day:
        user.current_streak = max(0, (user.current_streak or 0) + 1)
    else:
        user.current_streak = 1

    user.longest_streak = max(user.longest_streak or 0, user.current_streak or 0)
    user.last_active_date = active_day


def get_or_create_today_mission(db: Session, user_id: int, day_date: date) -> DailyMissionProgress:
    mission = (
        db.query(DailyMissionProgress)
        .filter(
            DailyMissionProgress.user_id == user_id,
            DailyMissionProgress.day_date == day_date,
        )
        .first()
    )
    if mission:
        return mission

    mission = DailyMissionProgress(
        user_id=user_id,
        day_date=day_date,
        target_sessions=MISSION_TARGET_SESSIONS,
        completed_sessions=0,
        bonus_xp_awarded=False,
    )
    db.add(mission)
    db.flush()
    return mission


def progress_mission_on_session_finish(db: Session, user: User, day_date: date) -> DailyMissionProgress:
    mission = get_or_create_today_mission(db, user.id, day_date)
    mission.completed_sessions = max(0, mission.completed_sessions + 1)

    if mission.completed_sessions >= mission.target_sessions and not mission.bonus_xp_awarded:
        mission.bonus_xp_awarded = True
        user.xp_total = max(0, (user.xp_total or 0) + MISSION_BONUS_XP)
        user.level = recalculate_level(user.xp_total)

    return mission


def get_mission_today(db: Session, user: User) -> DailyMissionProgress:
    return get_or_create_today_mission(db, user.id, today_for_user(user))


def _xp_curve_info(xp_total: int) -> dict[str, int]:
    # Keep legacy level formula for compatibility and show clearer level progress.
    level = recalculate_level(xp_total)
    xp_floor = level * 100
    xp_next = (level + 1) * 100
    return {
        "level": level,
        "xp_in_level": max(0, xp_total - xp_floor),
        "xp_to_next_level": max(0, xp_next - xp_total),
        "next_level": min(10, level + 1),
    }


def weekly_progress(db: Session, user: User, days: int = 7) -> list[dict]:
    today = today_for_user(user)
    start_day = today - timedelta(days=days - 1)
    start_dt = datetime.combine(start_day, datetime.min.time())
    sessions = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == user.id,
            StudySession.finished_at.is_not(None),
            StudySession.started_at >= start_dt,
        )
        .all()
    )

    buckets: dict[date, dict[str, int]] = defaultdict(lambda: {"sessions_count": 0, "minutes_studied": 0, "xp_earned": 0})
    for session in sessions:
        finished_day = session.finished_at.date()
        duration = max(1, int((session.finished_at - session.started_at).total_seconds() // 60))
        buckets[finished_day]["sessions_count"] += 1
        buckets[finished_day]["minutes_studied"] += duration
        buckets[finished_day]["xp_earned"] += max(0, session.xp_earned or 0)

    result = []
    for i in range(days):
        day = start_day + timedelta(days=i)
        values = buckets[day]
        result.append(
            {
                "date": day,
                "sessions_count": values["sessions_count"],
                "minutes_studied": values["minutes_studied"],
                "xp_earned": values["xp_earned"],
            }
        )
    return result


def weekly_leaderboard(db: Session, limit: int = 10, target_language_code: str | None = None) -> list[dict]:
    end_dt = datetime.now(UTC).replace(tzinfo=None)
    start_dt = end_dt - timedelta(days=7)

    query = (
        db.query(
            User.id.label("user_id"),
            User.name.label("name"),
            User.target_language_code.label("target_language_code"),
            func.coalesce(func.sum(StudySession.xp_earned), 0).label("xp_week"),
        )
        .join(StudySession, StudySession.user_id == User.id)
        .filter(
            StudySession.finished_at.is_not(None),
            StudySession.finished_at >= start_dt,
            StudySession.finished_at <= end_dt,
        )
        .group_by(User.id, User.name, User.target_language_code)
        .order_by(func.coalesce(func.sum(StudySession.xp_earned), 0).desc(), User.id.asc())
    )

    if target_language_code:
        query = query.filter(User.target_language_code == target_language_code)

    query = query.limit(limit)

    rows = query.all()
    return [
        {
            "rank": idx + 1,
            "user_id": int(row.user_id),
            "name": row.name,
            "xp_week": int(row.xp_week or 0),
            "target_language_code": row.target_language_code,
        }
        for idx, row in enumerate(rows)
    ]


def referral_status(db: Session, user: User) -> dict:
    code = ensure_referral_code(db, user)
    base_url = settings.frontend_url.rstrip("/")
    referral_link = f"{base_url}/?ref={code}"
    referred_count = max(0, user.referred_count or 0)
    reward_xp_total = referred_count * REFERRAL_BONUS_XP
    return {
        "referral_code": code,
        "referral_link": referral_link,
        "referred_count": referred_count,
        "reward_xp_total": reward_xp_total,
    }


def build_growth_dashboard(db: Session, user: User) -> dict:
    mission = get_mission_today(db, user)
    curve = _xp_curve_info(max(0, user.xp_total or 0))
    weekly = weekly_progress(db, user)
    leaderboard = weekly_leaderboard(db, limit=5, target_language_code=user.target_language_code)
    referral = referral_status(db, user)

    weekly_sessions_total = sum(item["sessions_count"] for item in weekly)
    weekly_minutes_total = sum(item["minutes_studied"] for item in weekly)
    weekly_xp_total = sum(item["xp_earned"] for item in weekly)

    return {
        "current_streak": max(0, user.current_streak or 0),
        "longest_streak": max(0, user.longest_streak or 0),
        "xp_total": max(0, user.xp_total or 0),
        "level": curve["level"],
        "xp_in_level": curve["xp_in_level"],
        "xp_to_next_level": curve["xp_to_next_level"],
        "next_level": curve["next_level"],
        "mission_today": {
            "day_date": mission.day_date,
            "target_sessions": mission.target_sessions,
            "completed_sessions": mission.completed_sessions,
            "is_completed": mission.completed_sessions >= mission.target_sessions,
            "bonus_xp_awarded": mission.bonus_xp_awarded,
        },
        "weekly_progress": weekly,
        "weekly_sessions_total": weekly_sessions_total,
        "weekly_minutes_total": weekly_minutes_total,
        "weekly_xp_total": weekly_xp_total,
        "leaderboard_top": leaderboard,
        "referral": referral,
    }
