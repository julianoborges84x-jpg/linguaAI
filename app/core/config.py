from __future__ import annotations

from typing import Any
from urllib.parse import urlparse, urlunparse

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _parse_list(value: Any, default: list[str]) -> list[str]:
    if value is None:
        return default
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    items = [item.strip() for item in str(value).split(",")]
    return [item for item in items if item]


def _normalize_local_redirect_url(url: str) -> str:
    """
    Guardrail for local environments: normalize legacy localhost:5173 redirects
    to localhost:3000 so checkout return matches the active frontend runtime.
    """
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host not in {"localhost", "127.0.0.1"}:
        return url

    if parsed.port != 5173:
        return url

    netloc_host = host
    if parsed.username and parsed.password:
        netloc_host = f"{parsed.username}:{parsed.password}@{host}"
    elif parsed.username:
        netloc_host = f"{parsed.username}@{host}"

    netloc = f"{netloc_host}:3000"
    return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "LinguaAI API"
    app_env: str = Field(default="development", validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT"))
    api_url: str = "http://127.0.0.1:8000"
    frontend_url: str = "http://localhost:3000"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/mentorlingua"
    db_auto_create: bool = False

    jwt_secret: str = "change-me"
    jwt_algorithm: str = Field(default="HS256", validation_alias=AliasChoices("JWT_ALGORITHM", "JWT_ALG"))
    jwt_exp_minutes: int = Field(
        default=60,
        validation_alias=AliasChoices("JWT_EXPIRES_MINUTES", "JWT_EXP_MINUTES", "ACCESS_TOKEN_EXPIRE_MINUTES"),
    )

    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    trusted_hosts: list[str] = ["localhost", "127.0.0.1", "testserver"]

    openai_api_key: str = ""
    llm_service_url: str = "http://localhost:8010"

    oauth_google_client_id: str = ""
    oauth_google_client_secret: str = ""
    oauth_apple_client_id: str = ""
    oauth_apple_team_id: str = ""
    oauth_apple_key_id: str = ""
    oauth_apple_private_key: str = ""

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None

    stripe_secret_key: str = ""
    stripe_publishable_key: str = Field(
        default="",
        validation_alias=AliasChoices("STRIPE_PUBLISHABLE_KEY", "STRIPE_PUBLISHBLE_KEY"),
    )
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""
    stripe_success_url: str = ""
    stripe_cancel_url: str = ""
    stripe_payment_method_types: str = "card"
    stripe_allow_fake_checkout: bool = False
    voice_free_limit: int = 6
    voice_free_daily_reset: bool = False

    @field_validator("jwt_exp_minutes", mode="before")
    @classmethod
    def _coerce_jwt_exp_minutes(cls, value: Any) -> int:
        return int(value or 60)

    @field_validator("db_auto_create", "stripe_allow_fake_checkout", "voice_free_daily_reset", mode="before")
    @classmethod
    def _coerce_bools(cls, value: Any) -> bool:
        return _parse_bool(value)

    @field_validator("voice_free_limit", mode="before")
    @classmethod
    def _coerce_voice_free_limit(cls, value: Any) -> int:
        parsed = int(value or 6)
        return max(4, min(6, parsed))

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def _coerce_cors_allowed_origins(cls, value: Any) -> list[str]:
        return _parse_list(
            value,
            default=[
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ],
        )

    @field_validator("trusted_hosts", mode="before")
    @classmethod
    def _coerce_trusted_hosts(cls, value: Any) -> list[str]:
        return _parse_list(value, default=["localhost", "127.0.0.1", "testserver"])

    @field_validator("stripe_publishable_key", mode="before")
    @classmethod
    def _fallback_publishable_key(cls, value: Any) -> str:
        return str(value or "")

    @field_validator("stripe_success_url", mode="before")
    @classmethod
    def _default_success_url(cls, value: Any) -> str:
        return str(value or "")

    @field_validator("stripe_cancel_url", mode="before")
    @classmethod
    def _default_cancel_url(cls, value: Any) -> str:
        return str(value or "")

    @property
    def effective_cors_origins(self) -> list[str]:
        origins = set(self.cors_allowed_origins)
        origins.add(self.frontend_url.rstrip("/"))
        return sorted(origins)

    @property
    def effective_trusted_hosts(self) -> list[str]:
        hosts = set(self.trusted_hosts)
        hosts.update({"localhost", "127.0.0.1", "testserver"})
        return sorted(hosts)

    @property
    def effective_stripe_success_url(self) -> str:
        raw_url = self.stripe_success_url or f"{self.frontend_url.rstrip('/')}/dashboard?checkout=success"
        return _normalize_local_redirect_url(raw_url)

    @property
    def effective_stripe_cancel_url(self) -> str:
        raw_url = self.stripe_cancel_url or f"{self.frontend_url.rstrip('/')}/dashboard?checkout=cancel"
        return _normalize_local_redirect_url(raw_url)

    @property
    def is_dev_like(self) -> bool:
        return self.app_env.strip().lower() in {"dev", "development", "test"}


settings = Settings()
