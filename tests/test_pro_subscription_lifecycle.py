import json

from app.core.config import settings
from app.models.user import PlanEnum, User


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_pro_subscription_full_lifecycle_uses_localhost_3000(client, db_session, monkeypatch):
    email = "pro-lifecycle@example.com"
    password = "123456"

    monkeypatch.setattr(settings, "app_env", "test")
    monkeypatch.setattr(settings, "frontend_url", "http://localhost:3000")
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_123")
    monkeypatch.setattr(settings, "stripe_price_id", "price_123")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")
    monkeypatch.setattr(settings, "stripe_success_url", "http://localhost:3000/dashboard?checkout=success")
    monkeypatch.setattr(settings, "stripe_cancel_url", "http://localhost:3000/dashboard?checkout=cancel")
    monkeypatch.setattr(settings, "stripe_allow_fake_checkout", False)

    class DummyCustomer:
        id = "cus_lifecycle_123"

    class DummyCheckoutSession:
        url = "https://checkout.stripe.test/session_lifecycle_123"

    class DummyPortalSession:
        url = "https://billing.stripe.test/portal_lifecycle_123"

    def fake_customer_create(*args, **kwargs):
        return DummyCustomer()

    def fake_checkout_session_create(**kwargs):
        # Valida URLs usadas no checkout
        assert kwargs["success_url"] == "http://localhost:3000/dashboard?checkout=success"
        assert kwargs["cancel_url"] == "http://localhost:3000/dashboard?checkout=cancel"
        return DummyCheckoutSession()

    def fake_portal_session_create(**kwargs):
        assert kwargs["return_url"] == "http://localhost:3000/dashboard?checkout=success"
        return DummyPortalSession()

    def fake_subscription_delete(subscription_id):
        assert subscription_id == "sub_lifecycle_123"
        return {"id": subscription_id, "status": "canceled"}

    def fake_construct_event(payload, sig_header, secret):
        return {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_lifecycle_123",
                    "subscription": "sub_lifecycle_123",
                    "metadata": {"user_id": str(user_id)},
                }
            },
        }

    monkeypatch.setattr("stripe.Customer.create", fake_customer_create)
    monkeypatch.setattr("stripe.checkout.Session.create", fake_checkout_session_create)
    monkeypatch.setattr("stripe.billing_portal.Session.create", fake_portal_session_create)
    monkeypatch.setattr("stripe.Subscription.delete", fake_subscription_delete)
    monkeypatch.setattr("stripe.Webhook.construct_event", fake_construct_event)

    # 1) Criar conta
    register = client.post(
        "/users",
        json={"name": "Ciclo Pro", "email": email, "password": password},
    )
    assert register.status_code == 201
    user_id = register.json()["id"]

    # 2) Login
    login = client.post("/auth/login", data={"username": email, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = _auth_header(token)

    # 3) Assinar PRO (criar checkout)
    checkout = client.post("/billing/create-checkout-session", headers=headers)
    assert checkout.status_code == 200
    checkout_url = checkout.json()["checkout_url"]
    assert checkout_url == "https://checkout.stripe.test/session_lifecycle_123"
    assert "5173" not in checkout_url

    # 4) Finalizar assinatura via webhook
    webhook = client.post("/billing/webhook", content=json.dumps({}), headers={"Stripe-Signature": "sig"})
    assert webhook.status_code == 200

    me_pro = client.get("/users/me", headers=headers)
    assert me_pro.status_code == 200
    assert me_pro.json()["plan"] == "PRO"

    status_pro = client.get("/billing/status", headers=headers)
    assert status_pro.status_code == 200
    assert status_pro.json()["plan"] == "PRO"
    assert status_pro.json()["subscription_status"] == "active"

    # 5) Gerenciar assinatura PRO
    portal = client.post("/billing/create-portal-session", headers=headers)
    assert portal.status_code == 200
    portal_url = portal.json()["portal_url"]
    assert portal_url == "https://billing.stripe.test/portal_lifecycle_123"
    assert "5173" not in portal_url

    # 6) Cancelar assinatura PRO
    cancel = client.post("/billing/cancel-subscription", headers=headers)
    assert cancel.status_code == 200
    assert cancel.json()["ok"] is True

    status_free = client.get("/billing/status", headers=headers)
    assert status_free.status_code == 200
    assert status_free.json()["plan"] == "FREE"

    user_db = db_session.query(User).filter(User.id == user_id).first()
    assert user_db is not None
    assert user_db.plan == PlanEnum.FREE
    assert user_db.subscription_status == "canceled"
