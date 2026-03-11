from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SessionStartIn(BaseModel):
    mode: Literal["chat", "vocab", "speaking", "writing"]
    topic_id: int | None = None


class SessionStartOut(BaseModel):
    session_id: int


class SessionFinishIn(BaseModel):
    interactions_count: int | None = None


class SessionFinishOut(BaseModel):
    session_id: int
    xp_earned: int
    interactions_count: int
    finished_at: datetime


class ProgressSummaryOut(BaseModel):
    xp_total: int
    level: int
    streak_days: int
    weekly_minutes: int
