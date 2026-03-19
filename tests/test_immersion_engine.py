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


def test_immersion_session_flow_and_dashboard(client):
    _, headers = _register_and_login(client, "immersion01@example.com")

    scenarios_res = client.get("/immersion/scenarios", headers=headers)
    assert scenarios_res.status_code == 200
    scenarios = scenarios_res.json()
    assert len(scenarios) >= 10
    first_slug = scenarios[0]["slug"]

    chars_res = client.get(f"/immersion/scenarios/{first_slug}/characters", headers=headers)
    assert chars_res.status_code == 200
    character_id = chars_res.json()[0]["id"] if chars_res.json() else None

    start_res = client.post(
        "/immersion/sessions/start",
        json={"scenario_slug": first_slug, "character_id": character_id, "source": "test"},
        headers=headers,
    )
    assert start_res.status_code == 200
    session_id = start_res.json()["session_id"]

    turn_res = client.post(
        f"/immersion/sessions/{session_id}/turn",
        json={"message": "um I has reservation for two people tonight."},
        headers=headers,
    )
    assert turn_res.status_code == 200
    assert turn_res.json()["turn_number"] >= 1
    assert len(turn_res.json()["hints"]) >= 1

    finish_res = client.post(f"/immersion/sessions/{session_id}/finish", headers=headers)
    assert finish_res.status_code == 200
    body = finish_res.json()
    assert body["fluency_score"] >= 0
    assert body["fluency_level"] in {"Turista", "Viajante", "Morador", "Profissional", "Especialista", "Nativo"}

    dashboard_res = client.get("/immersion/dashboard", headers=headers)
    assert dashboard_res.status_code == 200
    dashboard = dashboard_res.json()
    assert dashboard["latest_fluency_score"] >= 0
    assert "growth_loops" in dashboard


def test_immersion_missions_multiplayer_and_notifications(client):
    _, host_headers = _register_and_login(client, "host.challenge@example.com")
    _, guest_headers = _register_and_login(client, "guest.challenge@example.com")

    missions_res = client.get("/immersion/missions", headers=host_headers)
    assert missions_res.status_code == 200
    mission_id = missions_res.json()[0]["id"]

    claim_res = client.post(f"/immersion/missions/{mission_id}/claim", headers=host_headers)
    assert claim_res.status_code == 200
    assert claim_res.json()["status"] == "completed"
    assert claim_res.json()["new_xp_total"] >= claim_res.json()["xp_reward"]

    challenge_create = client.post(
        "/immersion/multiplayer/challenges",
        json={"scenario_slug": "reuniao"},
        headers=host_headers,
    )
    assert challenge_create.status_code == 200
    challenge_id = challenge_create.json()["challenge_id"]

    challenge_join = client.post(f"/immersion/multiplayer/challenges/{challenge_id}/join", headers=guest_headers)
    assert challenge_join.status_code == 200
    assert challenge_join.json()["status"] == "in_progress"

    notif_res = client.post("/immersion/notifications/sync", headers=host_headers)
    assert notif_res.status_code == 200
    assert "queued" in notif_res.json()
    assert "triggers" in notif_res.json()
