from app.core.config import settings


def create_user_and_token(client, email="dash@example.com", password="123"):
    register = client.post(
        "/users",
        json={"name": "Dash User", "email": email, "password": password},
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return register.json(), {"Authorization": f"Bearer {token}"}


def test_auth_login_success(client):
    _, headers = create_user_and_token(client, "auth-login@example.com")
    assert headers["Authorization"].startswith("Bearer ")


def test_users_me_requires_auth(client):
    res = client.get("/users/me")
    assert res.status_code == 401


def test_users_me_ok(client):
    _, headers = create_user_and_token(client, "users-me@example.com")
    res = client.get("/users/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "users-me@example.com"


def test_patch_users_me_updates_timezone_and_language(client):
    _, headers = create_user_and_token(client, "patch-me-dash@example.com")
    payload = {"timezone": "America/Sao_Paulo", "target_language": "en"}

    res = client.patch("/users/me", headers=headers, json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["timezone"] == "America/Sao_Paulo"
    assert body["target_language"] == "en"

    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["timezone"] == "America/Sao_Paulo"
    assert me.json()["target_language"] == "en"


def test_patch_users_me_rejects_partial_payload(client):
    _, headers = create_user_and_token(client, "partial-update@example.com")
    res = client.patch("/users/me", headers=headers, json={"target_language": "en"})
    assert res.status_code == 422


def test_streak_returns_int(client):
    _, headers = create_user_and_token(client, "streak-int@example.com")
    res = client.get("/daily-message/streak", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json()["streak"], int)


def test_weekly_progress_shape(client):
    _, headers = create_user_and_token(client, "weekly-shape@example.com")
    res = client.get("/mentor/progress/weekly", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 7
    assert {"date", "label", "count"}.issubset(data[0].keys())


def test_billing_status_no_500(client, monkeypatch):
    _, headers = create_user_and_token(client, "billing-status@example.com")
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_price_id", "")

    res = client.get("/billing/status", headers=headers)
    assert res.status_code == 200
    assert "stripe_configured" in res.json()
    assert "plan" in res.json()


def test_create_checkout_session_returns_503_when_not_configured(client, monkeypatch):
    _, headers = create_user_and_token(client, "billing-checkout@example.com")
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_price_id", "")
    monkeypatch.setattr(settings, "stripe_allow_fake_checkout", False)

    res = client.post("/billing/create-checkout-session", headers=headers)
    assert res.status_code == 503
    assert res.json()["detail"] == "Stripe não configurado"


def test_create_checkout_session_requires_auth(client):
    res = client.post("/billing/create-checkout-session")
    assert res.status_code == 401

def test_create_checkout_session_returns_fake_url_in_dev_when_disabled(client, monkeypatch):
    _, headers = create_user_and_token(client, "billing-checkout-fake@example.com")
    monkeypatch.setattr(settings, "app_env", "dev")
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_price_id", "")
    monkeypatch.setattr(settings, "stripe_allow_fake_checkout", True)

    res = client.post("/billing/create-checkout-session", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert "checkout_url" in body
    assert body["checkout_url"].startswith("http://127.0.0.1:5173/billing/fake-checkout")
