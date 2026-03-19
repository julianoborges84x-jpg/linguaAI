from app.core.config import settings
from app.models.user import PlanEnum, User


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_login_subscribe_pro_and_use_for_5_minutes(client, db_session, monkeypatch):
    email = "pro-flow@example.com"
    password = "123"

    register = client.post(
        "/users",
        json={"name": "Fluxo PRO", "email": email, "password": password},
    )
    assert register.status_code == 201
    user_id = register.json()["id"]

    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = _auth_header(token)

    checkout = client.post("/billing/create-checkout-session", headers=headers)
    assert checkout.status_code == 200
    checkout_body = checkout.json()
    assert "checkout_url" in checkout_body
    assert "fake-checkout" in checkout_body["checkout_url"]

    def fake_construct_event(payload, sig_header, secret):
        return {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_test_123",
                    "subscription": "sub_test_123",
                    "metadata": {"user_id": str(user_id)},
                }
            },
        }

    monkeypatch.setattr("stripe.Webhook.construct_event", fake_construct_event)
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")

    webhook = client.post("/billing/webhook", content="{}", headers={"Stripe-Signature": "t"})
    assert webhook.status_code == 200

    me_after_webhook = client.get("/users/me", headers=headers)
    assert me_after_webhook.status_code == 200
    assert me_after_webhook.json()["plan"] == "PRO"

    prefs = client.patch(
        "/users/me",
        json={"target_language": "en", "timezone": "America/Sao_Paulo"},
        headers=headers,
    )
    assert prefs.status_code == 200

    monkeypatch.setattr("app.services.llm_client.generate_reply", lambda instructions, text: "ok")

    for _ in range(5):
        chat = client.post(
            "/mentor/chat",
            json={"message": "treino de speaking", "feature": "speaking"},
            headers=headers,
        )
        assert chat.status_code == 200
        assert chat.json()["reply"] == "ok"

    user = db_session.query(User).filter(User.id == user_id).first()
    assert user is not None
    assert user.plan == PlanEnum.PRO
