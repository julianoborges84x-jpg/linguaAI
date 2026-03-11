from typing import Literal

from pydantic import BaseModel, Field


class UserPreferencesUpdate(BaseModel):
    target_language: Literal["en", "es", "fr", "it"]
    timezone: str = Field(min_length=1)
