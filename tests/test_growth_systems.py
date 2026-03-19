from datetime import UTC, datetime, timedelta
import importlib

from app.core.security import hash_password
from app.models.analytics_event import AnalyticsEvent
from app.models.study_session import StudySession
from app.models.user import PlanEnum, User
from app.services.growth_service import ensure_referral_code


def _register_and_login(client, email: str, password: str = "Teste123!"):
    created = client.post(
        "/users",
        json={"name": email.split("@")[0], "email": email, "password": password},
    )
    assert created.status_code == 201

    login = client.post("/auth/login", data={"username": email, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return created.json(), {"Authorization": f"Bearer {token}"}


def test_growth_dashboard_updates_streak_mission_and_events(client, db_session):
    _, headers = _register_and_login(client, "growth1@example.com")

    topics = client.get("/sessions/topics", headers=headers)
    assert topics.status_code == 200
    topic_id = topics.json()[0]["id"]

    started = client.post("/sessions/start", json={"mode": "writing", "topic_id": topic_id}, headers=headers)
    assert started.status_code == 200
    session_id = started.json()["session_id"]

    finished = client.post(f"/sessions/{session_id}/finish", json={"interactions_count": 4}, headers=headers)
    assert finished.status_code == 200
    assert finished.json()["xp_earned"] > 0

    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["current_streak"] >= 1
    assert me.json()["longest_streak"] >= 1

    dashboard = client.get("/growth/dashboard", headers=headers)
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["mission_today"]["is_completed"] is True
    assert body["weekly_sessions_total"] >= 1
    assert body["weekly_xp_total"] >= finished.json()["xp_earned"]

    events = db_session.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == me.json()["id"]).all()
    event_types = {event.event_type for event in events}
    assert {"login_success", "lesson_started", "lesson_completed", "streak_updated"}.issubset(event_types)


def test_referral_conversion_rewards_referrer_and_status(client):
    _, ref_headers = _register_and_login(client, "referrer@example.com")
    referral_status = client.get("/growth/referral", headers=ref_headers)
    assert referral_status.status_code == 200
    referral_code = referral_status.json()["referral_code"]

    referred = client.post(
        "/users",
        json={
            "name": "Referred User",
            "email": "referred@example.com",
            "password": "Teste123!",
            "referral_code": referral_code,
        },
    )
    assert referred.status_code == 201

    ref_me = client.get("/users/me", headers=ref_headers)
    assert ref_me.status_code == 200
    assert ref_me.json()["referred_count"] == 1
    assert ref_me.json()["xp_total"] >= 150


def test_weekly_leaderboard_orders_by_xp(client, db_session):
    user_a = User(
        name="Alice",
        email="alice@example.com",
        password_hash=hash_password("Teste123!"),
        plan=PlanEnum.FREE,
        level=1,
        xp_total=120,
        timezone="America/Sao_Paulo",
        onboarding_completed=True,
        target_language_code="en",
        referral_code="ALICE001",
    )
    user_b = User(
        name="Bruno",
        email="bruno@example.com",
        password_hash=hash_password("Teste123!"),
        plan=PlanEnum.FREE,
        level=1,
        xp_total=120,
        timezone="America/Sao_Paulo",
        onboarding_completed=True,
        target_language_code="en",
        referral_code="BRUNO001",
    )
    db_session.add_all([user_a, user_b])
    db_session.flush()

    now = datetime.now(UTC).replace(tzinfo=None)
    db_session.add_all(
        [
            StudySession(
                user_id=user_a.id,
                mode="writing",
                started_at=now - timedelta(minutes=10),
                finished_at=now - timedelta(minutes=5),
                interactions_count=3,
                xp_earned=50,
            ),
            StudySession(
                user_id=user_b.id,
                mode="writing",
                started_at=now - timedelta(minutes=20),
                finished_at=now - timedelta(minutes=10),
                interactions_count=5,
                xp_earned=80,
            ),
        ]
    )
    db_session.commit()

    login = client.post("/auth/login", data={"username": "alice@example.com", "password": "Teste123!"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    leaderboard = client.get("/growth/leaderboard/weekly", headers=headers)
    assert leaderboard.status_code == 200
    items = leaderboard.json()
    assert items[0]["name"] == "Bruno"
    assert items[0]["xp_week"] >= items[1]["xp_week"]


def test_public_growth_conversion_events_allowlisted(client, db_session):
    allowed = client.post(
        "/growth/events/public",
        json={"event_type": "hero_cta_click", "payload": {"variant": "a"}},
    )
    assert allowed.status_code == 201
    assert allowed.json()["event_type"] == "hero_cta_click"

    blocked = client.post(
        "/growth/events/public",
        json={"event_type": "random_event", "payload": {"x": 1}},
    )
    assert blocked.status_code == 422


def test_group_dashboard_legacy_routes_work_without_500(client):
    _, headers = _register_and_login(client, "legacygroup@example.com")

    canonical = client.get("/growth/dashboard", headers=headers)
    assert canonical.status_code == 200

    legacy = client.get("/group/dashboard", headers=headers)
    assert legacy.status_code == 200

    legacy_typo = client.get("/group/dasboard", headers=headers)
    assert legacy_typo.status_code == 200

    assert legacy.json()["level"] == canonical.json()["level"]
    assert legacy_typo.json()["xp_total"] == canonical.json()["xp_total"]


def test_growth_dashboard_persists_stable_referral_code_without_500(client):
    created, headers = _register_and_login(client, "stablegrowth@example.com")

    first = client.get("/growth/dashboard", headers=headers)
    assert first.status_code == 200
    first_referral = first.json()["referral"]["referral_code"]
    assert first_referral.startswith("lingua")
    assert len(first_referral) >= 8

    second = client.get("/growth/dashboard", headers=headers)
    assert second.status_code == 200
    second_referral = second.json()["referral"]["referral_code"]
    assert second_referral == first_referral

    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["id"] == created["id"]
    assert me.json()["referral_code"] == first_referral


def test_growth_dashboard_returns_fallback_payload_on_unexpected_error(client, monkeypatch):
    _, headers = _register_and_login(client, "growth-fallback@example.com")

    def _boom(*_args, **_kwargs):
        raise RuntimeError("boom")

    growth_module = importlib.import_module("app.api.routes.growth")
    monkeypatch.setattr(growth_module, "build_growth_dashboard", _boom)
    response = client.get("/growth/dashboard", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["mission_today"]["target_sessions"] == 1
    assert isinstance(payload["weekly_progress"], list)
    assert "referral" in payload


def test_ensure_referral_code_recovers_from_conflicting_in_memory_code(db_session):
    owner = User(
        name="Owner",
        email="owner-growth@example.com",
        password_hash=hash_password("Teste123!"),
        plan=PlanEnum.FREE,
        level=1,
        xp_total=0,
        timezone="America/Sao_Paulo",
        onboarding_completed=True,
        target_language_code="en",
        referral_code="linguax1234",
    )
    target = User(
        name="Target",
        email="target-growth@example.com",
        password_hash=hash_password("Teste123!"),
        plan=PlanEnum.FREE,
        level=1,
        xp_total=0,
        timezone="America/Sao_Paulo",
        onboarding_completed=True,
        target_language_code="en",
        referral_code=None,
    )
    db_session.add_all([owner, target])
    db_session.flush()

    # Simulate stale/conflicting value kept in-memory after rollback.
    target.referral_code = "linguax1234"
    resolved = ensure_referral_code(db_session, target)

    assert resolved != "linguax1234"
    assert resolved.startswith("lingua")
