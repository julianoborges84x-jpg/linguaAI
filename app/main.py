import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import auth, users, features, mentor, languages, daily_messages, motivation, billing
from app.core.config import settings
from app.core.database import Base, engine
from app.core.middleware import AuthMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("linguaai")

app = FastAPI(title=settings.app_name)
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

@app.get("/")
def root():
    return {"status": "ok", "service": "LinguaAI"}

@app.on_event("startup")
def on_startup():
    if settings.db_auto_create:
        logger.warning("DB_AUTO_CREATE=true: creating all tables on startup")
        Base.metadata.create_all(bind=engine)
    else:
        logger.info("DB_AUTO_CREATE=false: skipping Base.metadata.create_all")


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(auth)
app.include_router(users)
app.include_router(features)
app.include_router(mentor)
app.include_router(languages)
app.include_router(daily_messages)
app.include_router(motivation)
app.include_router(billing)
