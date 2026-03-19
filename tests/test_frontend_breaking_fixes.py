from app.core.config import settings


def create_user_and_token(client, email="frontend-fixes@example.com", password="123"):
    register = client.post(
        "/users",
        json={"name": "Frontend Fixes", "email": email, "password": password},
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_cors_preflight(client):
    response = client.options(
        "/users/me",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_auth_bearer_token(client):
    unauthorized = client.get("/users/me")
    assert unauthorized.status_code == 401

    headers = create_user_and_token(client, "auth-bearer-token@example.com")
    authorized = client.get("/users/me", headers=headers)
    assert authorized.status_code == 200
    assert authorized.json()["email"] == "auth-bearer-token@example.com"


def test_legacy_user_me_endpoint_keeps_backward_compatibility(client):
    unauthorized = client.get("/user/me")
    assert unauthorized.status_code == 401

    headers = create_user_and_token(client, "legacy-user-me@example.com")
    authorized = client.get("/user/me", headers=headers)
    assert authorized.status_code == 200
    assert authorized.json()["email"] == "legacy-user-me@example.com"


def test_legacy_user_me_patch_keeps_backward_compatibility(client):
    headers = create_user_and_token(client, "legacy-user-me-patch@example.com")

    response = client.patch(
        "/user/me",
        headers=headers,
        json={"target_language": "en", "timezone": "America/Sao_Paulo"},
    )
    assert response.status_code == 200
    assert response.json()["target_language"] == "en"
    assert response.json()["timezone"] == "America/Sao_Paulo"


def test_billing_create_checkout_session_stripe_not_configured(client, monkeypatch):
    headers = create_user_and_token(client, "billing-not-configured@example.com")
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_*****_me")
    monkeypatch.setattr(settings, "stripe_price_id", "")
    monkeypatch.setattr(settings, "stripe_allow_fake_checkout", False)

    response = client.post("/billing/create-checkout-session", headers=headers)
    assert response.status_code == 503
    assert response.json()["detail"] == "Stripe não configurado"
