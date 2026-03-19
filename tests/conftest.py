import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import get_db
from app.core.database import Base
from app.core.security import hash_password
from app.main import app as fastapi_app
from app import models  # noqa: F401
from app.models.user import PlanEnum, User


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture()
def db_session(engine, monkeypatch):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    monkeypatch.setattr("app.core.database.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("app.core.middleware.SessionLocal", TestingSessionLocal)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    settings.db_auto_create = False
    settings.app_env = "test"
    settings.frontend_url = "http://localhost:3000"
    settings.api_url = "http://127.0.0.1:8000"
    settings.stripe_secret_key = ""
    settings.stripe_price_id = ""
    settings.stripe_webhook_secret = ""
    settings.stripe_allow_fake_checkout = True
    settings.smtp_host = None
    settings.smtp_user = None
    settings.smtp_password = None
    settings.email_from = None
    if not settings.openai_api_key:
        settings.openai_api_key = "test-key"

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as client:
        yield client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def seed_user(db_session):
    user = User(
        name="Seed User",
        email="seed@example.com",
        password_hash=hash_password("123"),
        plan=PlanEnum.FREE,
        level=0,
        timezone="UTC",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def free_user(db_session):
    user = User(
        name="Free Test User",
        email="free_test@example.com",
        password_hash=hash_password("Teste123!"),
        plan=PlanEnum.FREE,
        level=1,
        xp_total=120,
        timezone="America/Sao_Paulo",
        onboarding_completed=True,
        target_language_code="en",
        target_language="en",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user.plain_password = "Teste123!"
    return user


@pytest.fixture()
def pro_user(db_session):
    user = User(
        name="Pro Test User",
        email="pro_test@example.com",
        password_hash=hash_password("Teste123!"),
        plan=PlanEnum.PRO,
        level=5,
        xp_total=1400,
        timezone="America/Sao_Paulo",
        onboarding_completed=True,
        target_language_code="en",
        target_language="en",
        subscription_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user.plain_password = "Teste123!"
    return user
