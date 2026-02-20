from pydantic import BaseModel, Field
from typing import Literal


class MotivationEventIn(BaseModel):
    type: Literal["level_up", "exercise_completed", "streak_check"]
    new_level: int | None = Field(default=None, ge=0, le=10)


class MotivationOut(BaseModel):
    quote: str | None = None
    category: str | None = None
