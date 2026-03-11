from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    plan: Literal["FREE", "PRO"]
    xp_total: int
    level: int
    timezone: str
    onboarding_completed: bool
    target_language: str | None = None
    language: str | None = None
    target_language_code: str | None = None
    base_language_code: str | None = None
    subscription_status: str | None = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    plan: Literal["FREE", "PRO"] | None = None
    level: int | None = None
    timezone: str | None = None
    target_language: str | None = None
    language: str | None = None
    target_language_code: str | None = None
    base_language_code: str | None = None


class UserPreferencesOut(BaseModel):
    target_language_code: str | None = None
    timezone: str
    onboarding_completed: bool


class UserPreferencesUpdate(BaseModel):
    target_language_code: str = Field(min_length=2, max_length=8)
    timezone: str = Field(min_length=1, max_length=64)
