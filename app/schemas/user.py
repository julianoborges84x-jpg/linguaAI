from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if value is None or value == "":
            raise ValueError("Password must not be empty.")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return value


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    plan: Literal["FREE", "PRO"]
    level: int
    timezone: str
    target_language_code: str | None = None
    base_language_code: str | None = None
    subscription_status: str | None = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    plan: Literal["FREE", "PRO"] | None = None
    level: int | None = Field(default=None, ge=0, le=10)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    target_language_code: str | None = None
    base_language_code: str | None = None
