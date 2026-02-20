import stripe
from app.core.config import settings

stripe.api_key = settings.stripe_secret_key


def create_customer(email: str, user_id: int, name: str | None = None) -> str:
    customer = stripe.Customer.create(
        email=email,
        name=name,
        metadata={"user_id": str(user_id)},
    )
    return customer.id


def create_checkout_session(customer_id: str, user_id: int) -> str:
    payment_method_types = None
    if settings.stripe_payment_method_types:
        payment_method_types = [m.strip() for m in settings.stripe_payment_method_types.split(",") if m.strip()]

    params = dict(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url=settings.stripe_success_url,
        cancel_url=settings.stripe_cancel_url,
        subscription_data={"metadata": {"user_id": str(user_id)}},
        metadata={"user_id": str(user_id)},
    )
    if payment_method_types:
        params["payment_method_types"] = payment_method_types

    session = stripe.checkout.Session.create(**params)
    return session.url


def cancel_subscription(subscription_id: str) -> None:
    stripe.Subscription.delete(subscription_id)


def create_customer_portal_session(customer_id: str) -> str:
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=settings.stripe_success_url,
    )
    return session.url
