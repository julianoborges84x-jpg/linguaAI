from fastapi import APIRouter, Depends

from app.core.deps import require_pro_user
from app.models.user import User

router = APIRouter(prefix="/features", tags=["features"])


@router.get("/writing")
def writing():
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
def ads():
    return {"feature": "ads"}
