from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import stripe

from app.core.config import settings
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User, PlanEnum
from app.services.stripe_service import (
    create_customer,
    create_checkout_session,
    cancel_subscription,
    create_customer_portal_session,
)

router = APIRouter(prefix="", tags=["billing"])


@router.post("/create-checkout-session")
def create_checkout(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not settings.stripe_secret_key or not settings.stripe_price_id:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    if not user.stripe_customer_id:
        customer_id = create_customer(user.email, user.id, user.name)
        user.stripe_customer_id = customer_id
        db.commit()
        db.refresh(user)

    url = create_checkout_session(user.stripe_customer_id, user.id)
    return {"checkout_url": url}


@router.post("/subscribe")
def subscribe_alias(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return create_checkout(db, user)


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.stripe_webhook_secret,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Webhook error: {exc}")

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        user_id = data.get("metadata", {}).get("user_id")
        if not user_id:
            return {"ok": True}
        user = db.query(User).filter(User.id == int(user_id)).first()
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
        user_id = data.get("metadata", {}).get("user_id")

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
            if status in {"active", "trialing"}:
                user.plan = PlanEnum.PRO
            else:
                user.plan = PlanEnum.FREE
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


@router.post("/cancel-subscription")
def cancel_subscribe(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    if not user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    cancel_subscription(user.stripe_subscription_id)
    user.plan = PlanEnum.FREE
    user.subscription_status = "canceled"
    db.commit()
    return {"ok": True}


@router.post("/customer-portal")
def customer_portal(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer")

    url = create_customer_portal_session(user.stripe_customer_id)
    return {"portal_url": url}
