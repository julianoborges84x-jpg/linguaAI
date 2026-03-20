from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user, require_pro_user
from app.models.user import PlanEnum, User

router = APIRouter(prefix="/features", tags=["features"])


@router.get("/writing")
def writing(_: User = Depends(get_current_user)):
    return {"feature": "writing"}


@router.get("/speaking")
def speaking(_: User = Depends(require_pro_user)):
    return {"feature": "speaking"}


@router.get("/dialect")
def dialect(_: User = Depends(require_pro_user)):
    return {"feature": "dialect"}


@router.get("/fillers")
def fillers(_: User = Depends(require_pro_user)):
    return {"feature": "fillers"}


@router.get("/ads")
def ads(current_user: User = Depends(get_current_user)):
    if current_user.plan == PlanEnum.PRO:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuarios PRO nao recebem anuncios")
    return {"feature": "ads"}
