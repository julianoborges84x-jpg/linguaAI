from app.models.analytics_event import AnalyticsEvent


def _register_user(client, email: str, referral_code: str | None = None):
    payload = {
        "name": email.split("@")[0],
        "email": email,
        "password": "Teste123!",
    }
    if referral_code:
        payload["referral_code"] = referral_code
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    return response.json()


def _auth_headers(client, email: str):
    login = client.post("/auth/login", data={"username": email, "password": "Teste123!"})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_referral_endpoints_return_code_and_stats(client):
    _register_user(client, "owner@example.com")
    headers = _auth_headers(client, "owner@example.com")

    me = client.get("/referral/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["referral_code"].startswith("lingua")
    assert "/invite/" in me.json()["invite_link"]

    stats = client.get("/referral/stats", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["referral_count"] == 0
    assert stats.json()["reward_xp_total"] == 0
    assert stats.json()["invited_users"] == []


def test_referral_code_is_unique_per_user(client):
    _register_user(client, "unique_a@example.com")
    _register_user(client, "unique_b@example.com")

    a_headers = _auth_headers(client, "unique_a@example.com")
    b_headers = _auth_headers(client, "unique_b@example.com")

    code_a = client.get("/referral/me", headers=a_headers).json()["referral_code"]
    code_b = client.get("/referral/me", headers=b_headers).json()["referral_code"]

    assert code_a
    assert code_b
    assert code_a != code_b


def test_referral_apply_blocks_self_and_is_idempotent(client):
    _register_user(client, "self@example.com")
    headers = _auth_headers(client, "self@example.com")
    referral_code = client.get("/referral/me", headers=headers).json()["referral_code"]

    self_apply = client.post("/referral/apply", headers=headers, json={"referral_code": referral_code})
    assert self_apply.status_code == 200
    assert self_apply.json()["applied"] is False
    assert self_apply.json()["referred_by"] is None

    second_apply = client.post("/referral/apply", headers=headers, json={"referral_code": referral_code})
    assert second_apply.status_code == 200
    assert second_apply.json()["applied"] is False


def test_referral_registration_rewards_both_and_updates_users_me(client, db_session):
    _register_user(client, "referrer@example.com")
    ref_headers = _auth_headers(client, "referrer@example.com")
    referral_code = client.get("/referral/me", headers=ref_headers).json()["referral_code"]

    _register_user(client, "newuser@example.com", referral_code=referral_code)
    new_headers = _auth_headers(client, "newuser@example.com")

    ref_me = client.get("/users/me", headers=ref_headers)
    assert ref_me.status_code == 200
    assert ref_me.json()["referred_count"] == 1
    assert ref_me.json()["referral_count"] == 1
    assert ref_me.json()["xp_total"] >= 150
    assert ref_me.json()["pro_access_until"] is not None

    new_me = client.get("/users/me", headers=new_headers)
    assert new_me.status_code == 200
    assert new_me.json()["referred_by"] == ref_me.json()["id"]
    assert new_me.json()["xp_total"] >= 150
    assert new_me.json()["pro_access_until"] is not None

    stats = client.get("/referral/stats", headers=ref_headers)
    assert stats.status_code == 200
    assert stats.json()["referral_count"] == 1
    assert stats.json()["reward_xp_total"] >= 150
    assert any(item["email"] == "newuser@example.com" for item in stats.json()["invited_users"])

    event_types = {
        item.event_type
        for item in db_session.query(AnalyticsEvent).all()
    }
    assert "referral_signup" in event_types
    assert "referral_reward_granted" in event_types
