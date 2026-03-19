from datetime import date, datetime

from pydantic import BaseModel


class DailyChallengeOut(BaseModel):
    day_date: date
    challenge_title: str
    scenario: str
    difficulty_level: int
    attempts_today: int
    best_score_today: int
    can_play_without_penalty: bool
    daily_badge_earned: bool


class DailyChallengeStartOut(BaseModel):
    challenge_id: int
    day_date: date
    challenge_title: str
    scenario: str
    attempt_number: int
    penalty_percent: int
    session_id: int
    character_role: str
    difficulty_level: int
    pressure_seconds: int
    opening_message: str
    started_at: datetime


class DailyChallengeSubmitIn(BaseModel):
    challenge_id: int


class DailyChallengeSubmitOut(BaseModel):
    challenge_id: int
    status: str
    score: int
    xp_awarded: int
    bonus_breakdown: dict[str, int]
    badge_awarded: bool
    attempts_today: int
    best_score_today: int
    finished_at: datetime
