from datetime import datetime

from pydantic import BaseModel


class RealLifeSessionIn(BaseModel):
    scenario: str
    retry_session_id: int | None = None


class RealLifeSessionOut(BaseModel):
    session_id: int
    scenario: str
    character_role: str
    difficulty_level: int
    pressure_seconds: int
    opening_message: str


class RealLifeMessageIn(BaseModel):
    session_id: int
    message: str
    response_time_seconds: int | None = None


class RealLifeFeedbackOut(BaseModel):
    correction: str
    better_response: str
    pressure_note: str
    level_adaptation: str


class RealLifeMessageOut(BaseModel):
    session_id: int
    status: str
    ai_question: str
    feedback: RealLifeFeedbackOut
    difficulty_level: int
    pressure_seconds: int
    turns_count: int
    xp_awarded: int
    bonus_breakdown: dict[str, int]
    total_xp_session: int
    updated_at: datetime
