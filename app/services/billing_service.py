import stripe
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import PlanEnum, User
from app.services import stripe_service


class BillingConfigError(Exception):
    pass


class BillingRequestError(Exception):
    pass


def _looks_like_placeholder_key(secret: str) -> bool:
    normalized = secret.strip()
    if not normalized:
        return True
    if "*" in normalized:
        return True
    return not (normalized.startswith("sk_test_") or normalized.startswith("sk_live_"))


def _is_dev_or_test() -> bool:
    return settings.app_env.strip().lower() in {"dev", "development", "test"}


def _fake_checkout_enabled() -> bool:
    return _is_dev_or_test() and bool(settings.stripe_allow_fake_checkout)


def _not_configured_message() -> str:
    return "Stripe não configurado"


def _require_stripe_enabled(require_price: bool = False) -> None:
    if _looks_like_placeholder_key(settings.stripe_secret_key):
        raise BillingConfigError(_not_configured_message())
    if require_price and not settings.stripe_price_id:
        raise BillingConfigError(_not_configured_message())


def create_checkout_session(db: Session, user: User) -> dict[str, str]:
    try:
        _require_stripe_enabled(require_price=True)
    except BillingConfigError:
        if _fake_checkout_enabled():
            return {
                "checkout_url": f"{settings.frontend_url.rstrip('/')}/billing/fake-checkout?user_id={user.id}",
                "mode": "fake",
            }
        raise
    if not user.stripe_customer_id:
        try:
            customer_id = stripe_service.create_customer(user.email, user.id, user.name)
        except stripe.error.StripeError as exc:
            raise BillingRequestError(f"Stripe request failed: {exc.user_message or str(exc)}") from exc
        user.stripe_customer_id = customer_id
        db.commit()
        db.refresh(user)

    try:
        url = stripe_service.create_checkout_session(user.stripe_customer_id, user.id)
    except stripe.error.StripeError as exc:
        raise BillingRequestError(f"Stripe request failed: {exc.user_message or str(exc)}") from exc
    return {"checkout_url": url}


def subscribe_user(db: Session, user: User) -> dict[str, str]:
    return create_checkout_session(db, user)


def cancel_subscription(db: Session, user: User) -> dict[str, bool]:
    _require_stripe_enabled()
    if not user.stripe_subscription_id:
        raise BillingRequestError("No active subscription")

    try:
        stripe_service.cancel_subscription(user.stripe_subscription_id)
    except stripe.error.StripeError as exc:
        raise BillingRequestError(f"Stripe request failed: {exc.user_message or str(exc)}") from exc
    user.plan = PlanEnum.FREE
    user.subscription_status = "canceled"
    db.commit()
    return {"ok": True}


def create_portal_session(user: User) -> dict[str, str]:
    _require_stripe_enabled()
    if not user.stripe_customer_id:
        raise BillingRequestError("No Stripe customer")

    try:
        url = stripe_service.create_customer_portal_session(user.stripe_customer_id)
    except stripe.error.StripeError as exc:
        raise BillingRequestError(f"Stripe request failed: {exc.user_message or str(exc)}") from exc
    return {"portal_url": url}


def handle_webhook(db: Session, payload: bytes, sig_header: str) -> dict[str, bool]:
    if not settings.stripe_webhook_secret:
        raise BillingConfigError("Stripe webhook not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.stripe_webhook_secret,
        )
    except Exception as exc:
        raise BillingRequestError(f"Webhook error: {exc}") from exc

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        metadata = data.get("metadata", {}) or {}
        user_id = metadata.get("user_id")
        user = None
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
        elif customer_id:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

        if user:
            user.plan = PlanEnum.PRO
            user.stripe_customer_id = customer_id
            user.stripe_subscription_id = subscription_id
            user.subscription_status = "active"
            db.commit()

    if event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        subscription_id = data.get("id")
        customer_id = data.get("customer")
        status = data.get("status")
        metadata = data.get("metadata", {}) or {}
        user_id = metadata.get("user_id")

        user = None
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
        elif subscription_id:
            user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        elif customer_id:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

        if user:
            user.stripe_customer_id = customer_id
            user.stripe_subscription_id = subscription_id
            user.subscription_status = status
            user.plan = PlanEnum.PRO if status in {"active", "trialing"} else PlanEnum.FREE
            db.commit()

    if event_type == "invoice.paid":
        subscription_id = data.get("subscription")
        customer_id = data.get("customer")
        user = None
        if subscription_id:
            user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        elif customer_id:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.plan = PlanEnum.PRO
            user.subscription_status = "active"
            db.commit()

    return {"ok": True}
