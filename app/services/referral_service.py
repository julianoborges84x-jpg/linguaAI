from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.services.growth_service import REFERRAL_BONUS_XP, apply_referral_if_valid, ensure_referral_code


def referral_me(db: Session, user: User) -> dict:
    code = ensure_referral_code(db, user)
    invite_link = f"{settings.frontend_url.rstrip('/')}/invite/{code}"
    return {
        "referral_code": code,
        "invite_link": invite_link,
        "pro_access_until": user.pro_access_until,
    }


def apply_referral(db: Session, user: User, referral_code: str) -> dict:
    before_referrer = user.referred_by_user_id
    apply_referral_if_valid(db, user, referral_code)
    applied = before_referrer is None and user.referred_by_user_id is not None
    db.commit()
    db.refresh(user)
    return {
        "applied": applied,
        "referred_by": user.referred_by_user_id,
        "xp_total": max(0, user.xp_total or 0),
        "level": max(0, user.level or 0),
        "pro_access_until": user.pro_access_until,
    }


def referral_stats(db: Session, user: User) -> dict:
    invited = (
        db.query(User)
        .filter(User.referred_by_user_id == user.id)
        .order_by(User.id.desc())
        .limit(50)
        .all()
    )
    referral_count = max(0, user.referred_count or 0)
    reward_xp_total = referral_count * REFERRAL_BONUS_XP
    return {
        "referral_count": referral_count,
        "reward_xp_total": reward_xp_total,
        "pro_access_until": user.pro_access_until,
        "invited_users": [
            {"user_id": item.id, "name": item.name, "email": item.email}
            for item in invited
        ],
    }
