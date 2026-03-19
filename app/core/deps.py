from fastapi import Depends, HTTPException, status
from datetime import date

from app.core.security import get_current_user, oauth2_scheme
from app.models.user import PlanEnum, User


def require_pro_user(current_user: User = Depends(get_current_user)) -> User:
    has_referral_pro = current_user.pro_access_until is not None and current_user.pro_access_until >= date.today()
    if current_user.plan != PlanEnum.PRO and not has_referral_pro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Upgrade para PRO para acessar este recurso",
        )
    return current_user


__all__ = ["get_current_user", "oauth2_scheme", "require_pro_user"]
