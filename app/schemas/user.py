from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal
from datetime import date


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    referral_code: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    google_sub: str | None = None
    apple_sub: str | None = None
    current_streak: int = 0
    longest_streak: int = 0
    last_active_date: date | None = None
    referral_code: str | None = None
    referred_count: int = 0
    referred_by: int | None = None
    referral_count: int = 0
    pro_access_until: date | None = None
    voice_messages_used: int = 0
    voice_usage_reset_at: date | None = None

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
