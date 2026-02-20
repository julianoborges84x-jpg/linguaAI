from fastapi import APIRouter

router = APIRouter(prefix="/features", tags=["features"])


@router.get("/writing")
def writing():
    return {"feature": "writing"}


@router.get("/speaking")
def speaking():
    return {"feature": "speaking"}


@router.get("/dialect")
def dialect():
    return {"feature": "dialect"}


@router.get("/fillers")
def fillers():
    return {"feature": "fillers"}


@router.get("/ads")
def ads():
    return {"feature": "ads"}
