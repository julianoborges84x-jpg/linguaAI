import json

from app.core.config import settings
from app.models.user import PlanEnum, User


def test_webhook_checkout_completed_sets_user_as_pro(client, db_session, monkeypatch):
    user = User(name="Webhook User", email="hook@example.com", password_hash="hash", plan=PlanEnum.FREE, level=0)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    def fake_construct_event(payload, sig_header, secret):
        return {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_checkout",
                    "subscription": "sub_checkout",
                    "metadata": {"user_id": str(user.id)},
                }
            },
        }

    monkeypatch.setattr("stripe.Webhook.construct_event", fake_construct_event)
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")

    response = client.post("/billing/webhook", data=json.dumps({}), headers={"Stripe-Signature": "sig"})
    assert response.status_code == 200

    updated = db_session.query(User).filter(User.id == user.id).first()
    assert updated is not None
    assert updated.plan == PlanEnum.PRO
    assert updated.subscription_status == "active"
    assert updated.stripe_subscription_id == "sub_checkout"


def test_webhook_subscription_deleted_downgrades_to_free(client, db_session, monkeypatch):
    user = User(
        name="Downgrade User",
        email="downgrade@example.com",
        password_hash="hash",
        plan=PlanEnum.PRO,
        level=5,
        stripe_customer_id="cus_sub",
        stripe_subscription_id="sub_to_cancel",
        subscription_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    def fake_construct_event(payload, sig_header, secret):
        return {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_to_cancel",
                    "customer": "cus_sub",
                    "status": "canceled",
                }
            },
        }

    monkeypatch.setattr("stripe.Webhook.construct_event", fake_construct_event)
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")

    response = client.post("/billing/webhook", data=json.dumps({}), headers={"Stripe-Signature": "sig"})
    assert response.status_code == 200

    updated = db_session.query(User).filter(User.id == user.id).first()
    assert updated is not None
    assert updated.plan == PlanEnum.FREE
    assert updated.subscription_status == "canceled"
