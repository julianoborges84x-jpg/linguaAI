import json

from app.core.config import settings
from app.models.user import PlanEnum, User


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

    res = client.post("/webhook", data=json.dumps({}), headers={"Stripe-Signature": "t"})
    assert res.status_code == 200

    updated = db_session.query(User).filter(User.id == user.id).first()
    assert updated.plan == PlanEnum.PRO
    assert updated.stripe_subscription_id == "sub_123"
    assert updated.subscription_status == "active"
