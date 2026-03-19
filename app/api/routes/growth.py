import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.growth import AnalyticsEventIn, AnalyticsEventOut, GrowthDashboardOut, LeaderboardItemOut, MissionTodayOut, ReferralStatusOut, WeeklyProgressItemOut
from app.services.analytics_service import track_event
from app.services.growth_service import build_growth_dashboard, get_mission_today, referral_status, weekly_leaderboard, weekly_progress
from app.services.progress_service import today_for_user

logger = logging.getLogger("linguaai.growth")

router = APIRouter(prefix="/growth", tags=["growth"])
legacy_router = APIRouter(prefix="/group", tags=["growth-legacy"])
PUBLIC_CONVERSION_EVENTS = {"hero_cta_click", "demo_cta_click", "final_cta_click", "landing_variant_exposed", "referral_link_opened"}


@router.get("/dashboard", response_model=GrowthDashboardOut)
def growth_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    def fallback_dashboard() -> dict:
        today = today_for_user(user)
        weekly = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            weekly.append({"date": day, "sessions_count": 0, "minutes_studied": 0, "xp_earned": 0})

        referral_code = (user.referral_code or f"lingua{str(user.id).zfill(5)[-5:]}").lower()
        referral_link = f"{settings.frontend_url.rstrip('/')}/?ref={referral_code}"
        xp_total = max(0, user.xp_total or 0)
        level = max(0, user.level or 0)

        return {
            "current_streak": max(0, user.current_streak or 0),
            "longest_streak": max(0, user.longest_streak or 0),
            "xp_total": xp_total,
            "level": level,
            "xp_in_level": max(0, xp_total - (level * 100)),
            "xp_to_next_level": max(0, ((level + 1) * 100) - xp_total),
            "next_level": min(10, level + 1),
            "mission_today": {
                "day_date": today,
                "target_sessions": 1,
                "completed_sessions": 0,
                "is_completed": False,
                "bonus_xp_awarded": False,
            },
            "weekly_progress": weekly,
            "weekly_sessions_total": 0,
            "weekly_minutes_total": 0,
            "weekly_xp_total": 0,
            "leaderboard_top": [],
            "referral": {
                "referral_code": referral_code,
                "referral_link": referral_link,
                "referred_count": max(0, user.referred_count or 0),
                "reward_xp_total": max(0, user.referred_count or 0) * 150,
            },
        }

    try:
        data = build_growth_dashboard(db, user)
        db.commit()
        return data
    except IntegrityError:
        # Retry once to recover from transient unique-conflicts (e.g. referral_code race).
        db.rollback()
        retry = build_growth_dashboard(db, user)
        db.commit()
        return retry
    except Exception as exc:
        db.rollback()
        logger.exception("growth dashboard failed for user_id=%s; returning fallback payload", user.id)
        return fallback_dashboard()


@legacy_router.get("/dashboard", response_model=GrowthDashboardOut, include_in_schema=False)
def growth_dashboard_legacy(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return growth_dashboard(db, user)


@legacy_router.get("/dasboard", response_model=GrowthDashboardOut, include_in_schema=False)
def growth_dashboard_legacy_typo(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Compatibility route for historical typo in some clients/logs.
    return growth_dashboard(db, user)


@router.get("/missions/today", response_model=MissionTodayOut)
def mission_today(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    mission = get_mission_today(db, user)
    db.commit()
    return MissionTodayOut(
        day_date=mission.day_date,
        target_sessions=mission.target_sessions,
        completed_sessions=mission.completed_sessions,
        is_completed=mission.completed_sessions >= mission.target_sessions,
        bonus_xp_awarded=mission.bonus_xp_awarded,
    )


@router.get("/progress/weekly", response_model=list[WeeklyProgressItemOut])
def progress_weekly(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return weekly_progress(db, user)


@router.get("/leaderboard/weekly", response_model=list[LeaderboardItemOut])
def leaderboard_weekly(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    target_language_code: str | None = Query(default=None),
):
    return weekly_leaderboard(db, limit=20, target_language_code=target_language_code)


@router.get("/referral", response_model=ReferralStatusOut)
def referral(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    payload = referral_status(db, user)
    db.commit()
    return payload


@router.post("/events", response_model=AnalyticsEventOut, status_code=201)
def collect_event(
    payload: AnalyticsEventIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    event = track_event(db, payload.event_type, user_id=user.id, payload=payload.payload)
    db.commit()
    db.refresh(event)
    return AnalyticsEventOut(id=event.id, event_type=event.event_type, created_at=event.created_at)


@router.post("/events/public", response_model=AnalyticsEventOut, status_code=201)
def collect_public_event(payload: AnalyticsEventIn, db: Session = Depends(get_db)):
    normalized = payload.event_type.strip().lower()
    if normalized not in PUBLIC_CONVERSION_EVENTS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unsupported public event type",
        )

    event = track_event(db, normalized, user_id=None, payload=payload.payload)
    db.commit()
    db.refresh(event)
    return AnalyticsEventOut(id=event.id, event_type=event.event_type, created_at=event.created_at)
