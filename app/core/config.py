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
    app_env: str = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development"))
    api_url: str = os.getenv("API_URL", "http://127.0.0.1:8000")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")

    # DATABASE
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5433/mentorlingua",
    )
    smtp_host: str = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", 587))
    smtp_user: str = os.getenv("SMTP_USER")
    smtp_password: str = os.getenv("SMTP_PASSWORD")
    email_from: str = os.getenv("EMAIL_FROM")

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
            "http://localhost:5173,http://127.0.0.1:5173",
        ),
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            os.getenv("FRONTEND_URL", "http://127.0.0.1:5173"),
        ],
    )

    # 🔥 CORREÇÃO PRINCIPAL AQUI
    trusted_hosts: list[str] = _parse_list(
    os.getenv(
        "TRUSTED_HOSTS",
        "localhost,127.0.0.1,testserver,linguaai-2.onrender.com",
    ),
    default=[
        "localhost",
        "127.0.0.1",
        "testserver",
        "linguaai-2.onrender.com",
    ],
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
        "STRIPE_SUCCESS_URL", f"{os.getenv('FRONTEND_URL', 'http://127.0.0.1:5173')}/dashboard?checkout=success"
    )
    stripe_cancel_url: str = os.getenv(
        "STRIPE_CANCEL_URL", f"{os.getenv('FRONTEND_URL', 'http://127.0.0.1:5173')}/dashboard?checkout=cancel"
    )
    stripe_payment_method_types: str = os.getenv(
        "STRIPE_PAYMENT_METHOD_TYPES", ""
    )
    stripe_allow_fake_checkout: bool = _parse_bool(
        os.getenv("STRIPE_ALLOW_FAKE_CHECKOUT"),
        default=os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development")).strip().lower() in {"dev", "development", "test"},
    )

print("DEBUG STRIPE_WEBHOOK_SECRET =", os.getenv("STRIPE_WEBHOOK_SECRET"))

settings = Settings()