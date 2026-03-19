from datetime import date

from app.core.config import settings
from app.models.language import Language
from app.services import daily_messages, llm_client


def register_user(client, name, email, password):
    return client.post(
        "/users",
        json={"name": name, "email": email, "password": password},
    )


def login_user(client, email, password):
    return client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def create_authenticated_user(client, email="regression@example.com", password="123"):
    register = register_user(client, "Regression User", email, password)
    assert register.status_code == 201

    login = login_user(client, email, password)
    assert login.status_code == 200
    token = login.json()["access_token"]
    return register.json(), token


def test_daily_message_streak_returns_success(client, monkeypatch):
    monkeypatch.setattr(daily_messages, "today_for_timezone", lambda tz: date(2024, 1, 5))
    monkeypatch.setattr(
        daily_messages,
        "load_passages",
        lambda: [{"id": "p1", "reference": "Ref", "text": "Text"}],
    )
    _, token = create_authenticated_user(client, "streak@example.com")

    today = client.get("/daily-message/today", headers=auth_header(token))
    assert today.status_code == 200

    streak = client.get("/daily-message/streak", headers=auth_header(token))
    assert streak.status_code == 200
    assert streak.json() == {"streak": 1}


def test_billing_endpoints_do_not_return_500_when_not_configured(client, monkeypatch):
    _, token = create_authenticated_user(client, "billing-unset@example.com")
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_price_id", "")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "")
    monkeypatch.setattr(settings, "stripe_allow_fake_checkout", False)

    checkout = client.post("/billing/create-checkout-session", headers=auth_header(token))
    assert checkout.status_code in (400, 503)

    cancel = client.post("/billing/cancel-subscription", headers=auth_header(token))
    assert cancel.status_code in (400, 503)

    portal = client.post("/billing/create-portal-session", headers=auth_header(token))
    assert portal.status_code in (400, 503)

    webhook = client.post("/billing/webhook", content="{}", headers={"Stripe-Signature": "sig"})
    assert webhook.status_code in (400, 503)


def test_patch_users_me_allows_partial_update(client, db_session):
    user_data, token = create_authenticated_user(client, "patch-me@example.com")
    db_session.add(Language(iso_code="eng", name="English", region="US", family="Indo-European"))
    db_session.commit()

    response = client.patch(
        "/users/me",
        headers=auth_header(token),
        json={"timezone": "America/Sao_Paulo", "target_language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == user_data["id"]
    assert body["timezone"] == "America/Sao_Paulo"
    assert body["target_language"] == "en"


def test_mentor_endpoints_work_with_mocked_llm(client, db_session, monkeypatch):
    db_session.add(Language(iso_code="por", name="Portuguese", region="BR", family="Indo-European"))
    db_session.add(Language(iso_code="eng", name="English", region="US", family="Indo-European"))
    db_session.commit()

    user_data, token = create_authenticated_user(client, "mentor-mocked@example.com")
    set_target = client.patch(
        f"/users/{user_data['id']}",
        json={"target_language_code": "eng"},
    )
    assert set_target.status_code == 200

    monkeypatch.setattr(llm_client, "detect_language", lambda text: "por")
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "mocked reply")

    detect = client.post(
        "/mentor/detect-language",
        headers=auth_header(token),
        json={"text": "Ola mundo"},
    )
    assert detect.status_code == 200
    assert detect.json()["iso_code"] == "por"

    chat = client.post(
        "/mentor/chat",
        headers=auth_header(token),
        json={"message": "Hello", "feature": "writing"},
    )
    assert chat.status_code == 200
    assert chat.json()["reply"] == "mocked reply"


def test_features_require_auth_and_allow_writing_for_authenticated_user(client):
    unauthorized = client.get("/features/writing")
    assert unauthorized.status_code == 401

    _, token = create_authenticated_user(client, "features@example.com")
    authorized = client.get("/features/writing", headers=auth_header(token))
    assert authorized.status_code == 200
    assert authorized.json() == {"feature": "writing"}


def test_cors_allows_localhost_3000(client):
    response = client.options(
        "/users",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_swagger_ui_and_openapi_are_available(client):
    docs = client.get("/docs")
    assert docs.status_code == 200
    assert "swagger-ui" in docs.text.lower()

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    schema = openapi.json()
    assert schema["openapi"].startswith("3.")
    assert schema["info"]["title"]
