from datetime import date, datetime

from pydantic import BaseModel


class MissionTodayOut(BaseModel):
    day_date: date
    target_sessions: int
    completed_sessions: int
    is_completed: bool
    bonus_xp_awarded: bool


class WeeklyProgressItemOut(BaseModel):
    date: date
    sessions_count: int
    minutes_studied: int
    xp_earned: int


class LeaderboardItemOut(BaseModel):
    rank: int
    user_id: int
    name: str
    xp_week: int
    target_language_code: str | None = None


class ReferralStatusOut(BaseModel):
    referral_code: str
    referral_link: str
    referred_count: int
    reward_xp_total: int


class GrowthDashboardOut(BaseModel):
    current_streak: int
    longest_streak: int
    xp_total: int
    level: int
    xp_in_level: int
    xp_to_next_level: int
    next_level: int
    mission_today: MissionTodayOut
    weekly_progress: list[WeeklyProgressItemOut]
    weekly_sessions_total: int
    weekly_minutes_total: int
    weekly_xp_total: int
    leaderboard_top: list[LeaderboardItemOut]
    referral: ReferralStatusOut


class AnalyticsEventIn(BaseModel):
    event_type: str
    payload: dict | None = None


class AnalyticsEventOut(BaseModel):
    id: int
    event_type: str
    created_at: datetime
