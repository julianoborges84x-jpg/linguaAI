import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import (
    auth,
    billing,
    daily_messages,
    features,
    languages,
    learna,
    mentor,
    motivation,
    sessions,
    users,
    users_legacy,
    growth,
    growth_legacy,
    immersion,
    real_life,
    daily_challenge,
    referral,
    pedagogy,
)
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.middleware import AuthMiddleware
from app.core.schema_compat import ensure_schema_compatibility
from app.services.billing_service import BillingConfigError, BillingRequestError, handle_webhook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("linguaai")


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.db_auto_create:
        logger.warning("DB_AUTO_CREATE=true is enabled. Prefer 'alembic upgrade head' for real environments.")
        Base.metadata.create_all(bind=engine)
    if settings.app_env.strip().lower() != "test":
        ensure_schema_compatibility(engine, log=logger.warning)

    logger.info("API booted in %s with CORS origins: %s", settings.app_env, ", ".join(settings.effective_cors_origins))
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.effective_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.effective_trusted_hosts if settings.trusted_hosts else ["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "LinguaAI"}


@app.get("/health", tags=["health"])
def health():
    db_ok = True
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
        logger.exception("Database healthcheck failed")
    return {"status": "ok" if db_ok else "degraded", "database": "ok" if db_ok else "error"}

@app.post("/webhook", include_in_schema=False)
async def legacy_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
):
    if not stripe_signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe-Signature header")

    payload = await request.body()
    db: Session = SessionLocal()
    try:
        return handle_webhook(db=db, payload=payload, sig_header=stripe_signature)
    except BillingConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except BillingRequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    finally:
        db.close()


app.include_router(auth)
app.include_router(users)
app.include_router(users_legacy)
app.include_router(features)
app.include_router(mentor)
app.include_router(languages)
app.include_router(daily_messages)
app.include_router(motivation)
app.include_router(learna)
app.include_router(sessions)
app.include_router(billing)
app.include_router(growth)
app.include_router(growth_legacy)
app.include_router(immersion)
app.include_router(real_life)
app.include_router(daily_challenge)
app.include_router(referral)
app.include_router(pedagogy)
