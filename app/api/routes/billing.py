from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.services.billing_service import (
    BillingConfigError,
    BillingRequestError,
    cancel_subscription as cancel_subscription_service,
    create_checkout_session,
    create_portal_session as create_portal_session_service,
    handle_webhook,
)
from app.services.analytics_service import track_event

router = APIRouter(prefix="/billing", tags=["billing"])


def _plan_value(plan) -> str:
    return plan.value if hasattr(plan, "value") else str(plan)


def _set_user_plan(user: User, plan_str: str) -> None:
    current_plan = getattr(user, "plan", None)
    if hasattr(current_plan, "value"):
        enum_type = type(current_plan)
        try:
            user.plan = enum_type(plan_str)  # type: ignore[misc]
            return
        except Exception:
            user.plan = plan_str  # type: ignore[assignment]
            return
    user.plan = plan_str  # type: ignore[assignment]


@router.get("/status")
def billing_status(user: User = Depends(get_current_user)) -> dict:
    secret = (settings.stripe_secret_key or "").strip()
    valid_key = bool(secret) and "*" not in secret and (secret.startswith("sk_test_") or secret.startswith("sk_live_"))
    configured = bool(valid_key and settings.stripe_price_id)
    return {
        "stripe_configured": configured,
        "plan": _plan_value(getattr(user, "plan", "FREE")),
        "subscription_status": getattr(user, "subscription_status", None),
    }


@router.post("/create-checkout-session")
def create_checkout(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    try:
        payload = create_checkout_session(db, user)
    except BillingConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except BillingRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    checkout_url = payload.get("checkout_url") or payload.get("url")
    if not checkout_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Checkout URL not returned",
        )

    return {
        "checkout_url": checkout_url,
        "url": checkout_url,
    }
@router.post("/create-portal-session")
def create_portal_session(
    user: User = Depends(get_current_user),
) -> dict:
    try:
        payload = create_portal_session_service(user)
    except BillingConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except BillingRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    portal_url = payload.get("portal_url") or payload.get("url")
    if not portal_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Portal URL not returned",
        )

    return {
        "portal_url": portal_url,
        "url": portal_url,
    }

@router.post("/fake/confirm")
def fake_confirm_subscription(
    user_id: int | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if not settings.stripe_allow_fake_checkout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    target_user_id = user_id if user_id is not None else user.id

    if user_id is not None and user_id != user.id:
        raise HTTPException(status_code=403, detail="user_id nao confere com o usuario logado")

    db_user = db.query(User).filter(User.id == target_user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    _set_user_plan(db_user, "PRO")
    if hasattr(db_user, "subscription_status"):
        setattr(db_user, "subscription_status", "active")
    track_event(db, "pro_checkout_completed", user_id=db_user.id, payload={"mode": "fake"})

    db.commit()
    db.refresh(db_user)

    return {
        "success": True,
        "user_id": db_user.id,
        "plan": _plan_value(db_user.plan),
        "subscription_status": getattr(db_user, "subscription_status", None),
    }


@router.post("/cancel-subscription")
def cancel_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = cancel_subscription_service(db, user)
    except BillingConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except BillingRequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.post("/webhook")
async def billing_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
) -> dict:
    if not stripe_signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe-Signature header")

    payload = await request.body()
    try:
        return handle_webhook(db=db, payload=payload, sig_header=stripe_signature)
    except BillingConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except BillingRequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
