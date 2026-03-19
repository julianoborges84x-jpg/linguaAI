from app.models.analytics_event import AnalyticsEvent


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


def test_real_life_start_and_message_awards_xp_and_tracks_started(client, db_session):
    user, headers = _register_and_login(client, "reallife-start@example.com")

    start = client.post("/real-life/session", headers=headers, json={"scenario": "restaurante"})
    assert start.status_code == 200
    session_id = start.json()["session_id"]
    assert start.json()["pressure_seconds"] > 0

    before = client.get("/users/me", headers=headers).json()["xp_total"]
    msg = client.post(
        "/real-life/message",
        headers=headers,
        json={
            "session_id": session_id,
            "message": "Could I order the grilled fish, please?",
            "response_time_seconds": 8,
        },
    )
    assert msg.status_code == 200
    body = msg.json()
    assert body["xp_awarded"] >= 20
    assert body["bonus_breakdown"]["quick"] >= 0
    assert body["feedback"]["better_response"]

    after = client.get("/users/me", headers=headers).json()["xp_total"]
    assert after >= before + body["xp_awarded"]

    events = db_session.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == user["id"]).all()
    types = {event.event_type for event in events}
    assert "real_life_started" in types


def test_real_life_retry_completed_and_failed_events(client, db_session):
    user, headers = _register_and_login(client, "reallife-retry@example.com")

    start = client.post("/real-life/session", headers=headers, json={"scenario": "aeroporto"})
    assert start.status_code == 200
    session_id = start.json()["session_id"]

    retry = client.post(
        "/real-life/session",
        headers=headers,
        json={"scenario": "aeroporto", "retry_session_id": session_id},
    )
    assert retry.status_code == 200
    retry_id = retry.json()["session_id"]

    completed = None
    for _ in range(7):
        resp = client.post(
            "/real-life/message",
            headers=headers,
            json={
                "session_id": retry_id,
                "message": "Could I check in now, please? I also need help with my bag.",
                "response_time_seconds": 5,
            },
        )
        assert resp.status_code == 200
        completed = resp.json()
        if completed["status"] != "active":
            break
    assert completed is not None
    assert completed["status"] in {"completed", "failed"}

    failed_start = client.post("/real-life/session", headers=headers, json={"scenario": "emergencia"})
    assert failed_start.status_code == 200
    failed_id = failed_start.json()["session_id"]
    failed = client.post(
        "/real-life/message",
        headers=headers,
        json={
            "session_id": failed_id,
            "message": "please help now quickly",
            "response_time_seconds": 100,
        },
    )
    assert failed.status_code == 200
    assert failed.json()["status"] == "failed"

    events = db_session.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == user["id"]).all()
    types = {event.event_type for event in events}
    assert "real_life_retry" in types
    assert "real_life_failed" in types
