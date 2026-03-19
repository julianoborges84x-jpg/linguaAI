import json

from app.core.config import settings
from app.models.user import PlanEnum, User
from app.core.security import hash_password


def _login_and_get_token(client, email: str, password: str) -> str:
    login = client.post("/auth/login", data={"username": email, "password": password})
    assert login.status_code == 200
    return login.json()["access_token"]


def test_webhook_updates_plan(client, db_session, monkeypatch):
    user = User(name="Pay User", email="pay@example.com", password_hash="hash", plan=PlanEnum.FREE, level=0)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    def fake_construct_event(payload, sig_header, secret):
        return {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_123",
                    "subscription": "sub_123",
                    "metadata": {"user_id": str(user.id)},
                }
            },
        }

    monkeypatch.setattr("stripe.Webhook.construct_event", fake_construct_event)
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")

    res = client.post("/billing/webhook", content=json.dumps({}), headers={"Stripe-Signature": "t"})
    assert res.status_code == 200

    updated = db_session.query(User).filter(User.id == user.id).first()
    assert updated.plan == PlanEnum.PRO
    assert updated.stripe_subscription_id == "sub_123"
    assert updated.subscription_status == "active"


def test_create_checkout_session_returns_fake_url_in_dev_test(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "app_env", "test")
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_price_id", "")
    monkeypatch.setattr(settings, "stripe_allow_fake_checkout", True)

    user = User(
        name="Checkout User",
        email="checkout@example.com",
        password_hash=hash_password("123"),
        plan=PlanEnum.FREE,
        level=0,
    )
    db_session.add(user)
    db_session.commit()

    token = _login_and_get_token(client, "checkout@example.com", "123")
    res = client.post(
        "/billing/create-checkout-session",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "checkout_url" in body
    assert "billing/fake-checkout" in body["checkout_url"]


def test_billing_status_returns_stripe_configured_and_plan(client, pro_user, monkeypatch):
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_123")
    monkeypatch.setattr(settings, "stripe_price_id", "price_123")
    token = _login_and_get_token(client, pro_user.email, pro_user.plain_password)

    res = client.get("/billing/status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    body = res.json()
    assert "stripe_configured" in body
    assert body["stripe_configured"] is True
    assert body["plan"] == "PRO"


def test_create_checkout_session_returns_checkout_url_for_free_user(client, free_user, monkeypatch):
    monkeypatch.setattr(settings, "app_env", "test")
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_price_id", "")
    monkeypatch.setattr(settings, "stripe_allow_fake_checkout", True)

    token = _login_and_get_token(client, free_user.email, free_user.plain_password)
    res = client.post("/billing/create-checkout-session", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    body = res.json()
    assert "checkout_url" in body
    assert body["checkout_url"]


def test_checkout_uses_localhost_3000_success_and_cancel_urls(client, free_user, monkeypatch):
    monkeypatch.setattr(settings, "app_env", "test")
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_123")
    monkeypatch.setattr(settings, "stripe_price_id", "price_123")
    monkeypatch.setattr(settings, "stripe_allow_fake_checkout", False)
    monkeypatch.setattr(settings, "frontend_url", "http://localhost:3000")
    monkeypatch.setattr(settings, "stripe_success_url", "http://localhost:3000/dashboard?checkout=success")
    monkeypatch.setattr(settings, "stripe_cancel_url", "http://localhost:3000/dashboard?checkout=cancel")

    captured = {}

    class DummyCustomer:
        id = "cus_test_123"

    class DummySession:
        url = "https://checkout.stripe.test/session_123"

    def fake_customer_create(*args, **kwargs):
        return DummyCustomer()

    def fake_session_create(**kwargs):
        captured.update(kwargs)
        return DummySession()

    monkeypatch.setattr("stripe.Customer.create", fake_customer_create)
    monkeypatch.setattr("stripe.checkout.Session.create", fake_session_create)

    token = _login_and_get_token(client, free_user.email, free_user.plain_password)
    res = client.post("/billing/create-checkout-session", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["checkout_url"] == "https://checkout.stripe.test/session_123"
    assert captured["success_url"] == "http://localhost:3000/dashboard?checkout=success"
    assert captured["cancel_url"] == "http://localhost:3000/dashboard?checkout=cancel"


def test_checkout_rewrites_legacy_localhost_5173_redirects_to_3000(client, free_user, monkeypatch):
    monkeypatch.setattr(settings, "app_env", "test")
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_123")
    monkeypatch.setattr(settings, "stripe_price_id", "price_123")
    monkeypatch.setattr(settings, "stripe_allow_fake_checkout", False)
    monkeypatch.setattr(settings, "frontend_url", "http://localhost:3000")
    monkeypatch.setattr(settings, "stripe_success_url", "http://localhost:5173/dashboard?checkout=success")
    monkeypatch.setattr(settings, "stripe_cancel_url", "http://localhost:5173/dashboard?checkout=cancel")

    captured = {}

    class DummyCustomer:
        id = "cus_test_5173"

    class DummySession:
        url = "https://checkout.stripe.test/session_5173"

    def fake_customer_create(*args, **kwargs):
        return DummyCustomer()

    def fake_session_create(**kwargs):
        captured.update(kwargs)
        return DummySession()

    monkeypatch.setattr("stripe.Customer.create", fake_customer_create)
    monkeypatch.setattr("stripe.checkout.Session.create", fake_session_create)

    token = _login_and_get_token(client, free_user.email, free_user.plain_password)
    res = client.post("/billing/create-checkout-session", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["checkout_url"] == "https://checkout.stripe.test/session_5173"
    assert captured["success_url"] == "http://localhost:3000/dashboard?checkout=success"
    assert captured["cancel_url"] == "http://localhost:3000/dashboard?checkout=cancel"
