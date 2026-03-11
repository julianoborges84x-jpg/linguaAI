from datetime import date, datetime, timedelta

from app.models.study_session import StudySession


def create_user_and_headers(client, email="sessions@example.com", password="123"):
    register = client.post(
        "/users",
        json={"name": "Session User", "email": email, "password": password},
    )
    assert register.status_code == 201

    login = client.post("/auth/login", data={"username": email, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_session_start_creates_session(client, db_session):
    headers = create_user_and_headers(client, "session-start@example.com")

    response = client.post("/sessions/start", headers=headers, json={"mode": "chat"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    assert isinstance(session_id, int)

    session = db_session.query(StudySession).filter(StudySession.id == session_id).first()
    assert session is not None
    assert session.mode == "chat"
    assert session.finished_at is None


def test_session_finish_awards_xp_and_updates_user(client, db_session):
    headers = create_user_and_headers(client, "session-finish@example.com")
    start = client.post("/sessions/start", headers=headers, json={"mode": "writing"})
    assert start.status_code == 200
    session_id = start.json()["session_id"]

    session = db_session.query(StudySession).filter(StudySession.id == session_id).first()
    session.started_at = datetime.utcnow() - timedelta(minutes=30)
    db_session.commit()

    finish = client.post(
        f"/sessions/{session_id}/finish",
        headers=headers,
        json={"interactions_count": 5},
    )
    assert finish.status_code == 200
    payload = finish.json()
    assert payload["xp_earned"] > 0
    assert payload["interactions_count"] == 5

    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    user_data = me.json()
    assert user_data["xp_total"] == payload["xp_earned"]
    assert user_data["level"] == min(10, user_data["xp_total"] // 100)


def test_streak_increases_on_consecutive_days(client, monkeypatch):
    headers = create_user_and_headers(client, "streak-consecutive@example.com")

    for day in [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)]:
        monkeypatch.setattr("app.services.session_service.today_for_user", lambda _user, d=day: d)
        started = client.post("/sessions/start", headers=headers, json={"mode": "chat"})
        session_id = started.json()["session_id"]
        finished = client.post(f"/sessions/{session_id}/finish", headers=headers, json={"interactions_count": 1})
        assert finished.status_code == 200

    monkeypatch.setattr("app.services.progress_service.today_for_user", lambda _user: date(2026, 1, 3))
    streak = client.get("/daily-message/streak", headers=headers)
    assert streak.status_code == 200
    assert streak.json()["streak"] == 3


def test_streak_resets_when_skip_day(client, monkeypatch):
    headers = create_user_and_headers(client, "streak-skip@example.com")

    for day in [date(2026, 1, 1), date(2026, 1, 3)]:
        monkeypatch.setattr("app.services.session_service.today_for_user", lambda _user, d=day: d)
        started = client.post("/sessions/start", headers=headers, json={"mode": "vocab"})
        session_id = started.json()["session_id"]
        finished = client.post(f"/sessions/{session_id}/finish", headers=headers)
        assert finished.status_code == 200

    monkeypatch.setattr("app.services.progress_service.today_for_user", lambda _user: date(2026, 1, 3))
    streak = client.get("/daily-message/streak", headers=headers)
    assert streak.status_code == 200
    assert streak.json()["streak"] == 1


def test_progress_summary_returns_consistent_fields(client, db_session):
    headers = create_user_and_headers(client, "summary@example.com")
    started = client.post("/sessions/start", headers=headers, json={"mode": "speaking"})
    session_id = started.json()["session_id"]

    session = db_session.query(StudySession).filter(StudySession.id == session_id).first()
    session.started_at = datetime.utcnow() - timedelta(minutes=45)
    db_session.commit()

    finished = client.post(
        f"/sessions/{session_id}/finish",
        headers=headers,
        json={"interactions_count": 3},
    )
    assert finished.status_code == 200

    summary = client.get("/progress/summary", headers=headers)
    assert summary.status_code == 200
    body = summary.json()
    assert {"xp_total", "level", "streak_days", "weekly_minutes"}.issubset(body.keys())
    assert body["xp_total"] >= finished.json()["xp_earned"]
    assert 0 <= body["level"] <= 10
    assert body["streak_days"] >= 1
    assert body["weekly_minutes"] >= 1
