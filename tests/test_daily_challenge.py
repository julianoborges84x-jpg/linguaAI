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


def test_daily_challenge_get_start_submit_flow(client, db_session):
    user, headers = _register_and_login(client, "daily-challenge@example.com")

    info = client.get("/daily-challenge", headers=headers)
    assert info.status_code == 200
    assert info.json()["challenge_title"]
    assert info.json()["attempts_today"] == 0

    started = client.post("/daily-challenge/start", headers=headers)
    assert started.status_code == 200
    payload = started.json()
    assert payload["challenge_id"] > 0
    assert payload["session_id"] > 0

    # Send a couple of real-life messages in the linked session.
    for _ in range(3):
        msg = client.post(
            "/real-life/message",
            headers=headers,
            json={
                "session_id": payload["session_id"],
                "message": "Could I order now, please? I would like a drink as well.",
                "response_time_seconds": 6,
            },
        )
        assert msg.status_code == 200

    submitted = client.post("/daily-challenge/submit", headers=headers, json={"challenge_id": payload["challenge_id"]})
    assert submitted.status_code == 200
    body = submitted.json()
    assert body["score"] >= 0
    assert body["xp_awarded"] >= 0
    assert body["status"] == "completed"

    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["xp_total"] >= 0

    events = db_session.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == user["id"]).all()
    event_types = {event.event_type for event in events}
    assert "daily_challenge_started" in event_types
    assert "daily_challenge_completed" in event_types
    assert "daily_challenge_score" in event_types


def test_daily_challenge_second_attempt_applies_penalty(client):
    _, headers = _register_and_login(client, "daily-penalty@example.com")

    first = client.post("/daily-challenge/start", headers=headers)
    assert first.status_code == 200
    assert first.json()["attempt_number"] == 1
    assert first.json()["penalty_percent"] == 0

    second = client.post("/daily-challenge/start", headers=headers)
    assert second.status_code == 200
    assert second.json()["attempt_number"] == 2
    assert second.json()["penalty_percent"] >= 10
