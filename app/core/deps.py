from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user, oauth2_scheme
from app.models.user import PlanEnum, User


def require_pro_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.plan != PlanEnum.PRO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Upgrade para PRO para acessar este recurso",
        )
    return current_user


__all__ = ["get_current_user", "oauth2_scheme", "require_pro_user"]
