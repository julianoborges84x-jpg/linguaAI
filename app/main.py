import logging

from fastapi import FastAPI
from fastapi import Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError
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
)
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.middleware import AuthMiddleware
from app.services.billing_service import BillingConfigError, BillingRequestError, handle_webhook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("linguaai")

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.trusted_hosts if settings.trusted_hosts else ["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "LinguaAI"}


@app.on_event("startup")
def on_startup():
    if settings.db_auto_create:
        logger.warning("DB_AUTO_CREATE=true: creating all tables on startup")
        try:
            Base.metadata.create_all(bind=engine)
        except ProgrammingError as exc:
            msg = str(exc).lower()
            if "already exists" in msg or "duplicatetable" in msg:
                logger.warning("Tables already exist. Ignoring...")
            else:
                raise
    else:
        logger.info("DB_AUTO_CREATE=false: skipping Base.metadata.create_all")


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

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
app.include_router(features)
app.include_router(mentor)
app.include_router(languages)
app.include_router(daily_messages)
app.include_router(motivation)
app.include_router(learna)
app.include_router(sessions)
app.include_router(billing)
