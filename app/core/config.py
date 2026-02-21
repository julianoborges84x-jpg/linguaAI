import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_list(value: str, default: list[str]) -> list[str]:
    if not value:
        return default
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]


class Settings(BaseModel):
    # APP
    app_name: str = "LinguaAI API"
    app_env: str = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "dev"))

    # DATABASE
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5433/mentorlingua",
    )

    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-dev")
    jwt_algorithm: str = os.getenv("JWT_ALG", os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_exp_minutes: int = int(
        os.getenv(
            "JWT_EXPIRES_MINUTES",
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", os.getenv("JWT_EXP_MINUTES", "60")),
        )
    )

    # CORS
    cors_allowed_origins: list[str] = _parse_list(
        os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,https://*.onrender.com",
        ),
        default=["http://localhost:5173"],
    )

    # 🔥 CORREÇÃO PRINCIPAL AQUI
    trusted_hosts: list[str] = _parse_list(
        os.getenv(
            "TRUSTED_HOSTS",
            "localhost,127.0.0.1,*.onrender.com",
        ),
        default=["localhost", "127.0.0.1", "*.onrender.com"],
    )

    # DB
    db_auto_create: bool = _parse_bool(os.getenv("DB_AUTO_CREATE"), default=False)

    # OPENAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # STRIPE
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_price_id: str = os.getenv("STRIPE_PRICE_ID", "")
    stripe_success_url: str = os.getenv(
        "STRIPE_SUCCESS_URL", "http://localhost:5173/dashboard"
    )
    stripe_cancel_url: str = os.getenv(
        "STRIPE_CANCEL_URL", "http://localhost:5173/dashboard"
    )
    stripe_payment_method_types: str = os.getenv(
        "STRIPE_PAYMENT_METHOD_TYPES", ""
    )


settings = Settings()
