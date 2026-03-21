def register_user(client, name, email, password):
    return client.post("/users", json={"name": name, "email": email, "password": password})


def login_user(client, email, password):
    return client.post("/auth/login", data={"username": email, "password": password})


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_realtime_session_start_requires_auth(client):
    res = client.post("/realtime/sessions/start", json={"mentor_id": "clara"})
    assert res.status_code == 401


def test_realtime_session_flow(client):
    register = register_user(client, "Realtime User", "realtime_user@example.com", "secret123")
    assert register.status_code == 201

    login = login_user(client, "realtime_user@example.com", "secret123")
    assert login.status_code == 200
    token = login.json()["access_token"]

    start = client.post(
        "/realtime/sessions/start",
        headers=auth_header(token),
        json={"mentor_id": "clara", "mode": "voice_video"},
    )
    assert start.status_code == 200
    payload = start.json()
    session_id = payload["session_id"]
    assert payload["status"] == "created"
    assert payload["beta"] is True
    assert payload["signaling_path"].endswith(f"/realtime/sessions/{session_id}/signal")
    assert len(payload["ice_servers"]) >= 1

    signal = client.post(
        f"/realtime/sessions/{session_id}/signal",
        headers=auth_header(token),
        json={"signal_type": "offer", "payload": {"sdp": "test-sdp"}},
    )
    assert signal.status_code == 200
    assert signal.json()["accepted"] is True
    assert signal.json()["status"] == "negotiating"

    stop = client.post(f"/realtime/sessions/{session_id}/stop", headers=auth_header(token))
    assert stop.status_code == 200
    assert stop.json()["status"] == "stopped"


def test_realtime_session_forbidden_for_another_user(client):
    register_user(client, "Owner", "realtime_owner@example.com", "secret123")
    token_owner = login_user(client, "realtime_owner@example.com", "secret123").json()["access_token"]
    start = client.post("/realtime/sessions/start", headers=auth_header(token_owner), json={"mentor_id": "clara"})
    session_id = start.json()["session_id"]

    register_user(client, "Other", "realtime_other@example.com", "secret123")
    token_other = login_user(client, "realtime_other@example.com", "secret123").json()["access_token"]
    forbidden = client.post(
        f"/realtime/sessions/{session_id}/signal",
        headers=auth_header(token_other),
        json={"signal_type": "offer", "payload": {"sdp": "x"}},
    )
    assert forbidden.status_code == 403
