from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.real_life import RealLifeMessageIn, RealLifeMessageOut, RealLifeSessionIn, RealLifeSessionOut
from app.services.real_life_service import send_real_life_message, start_real_life_session

router = APIRouter(prefix="/real-life", tags=["real-life"])


@router.post("/session", response_model=RealLifeSessionOut)
def start_session(
    payload: RealLifeSessionIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = start_real_life_session(db, user, scenario=payload.scenario, retry_session_id=payload.retry_session_id)
    return RealLifeSessionOut(**data)


@router.post("/message", response_model=RealLifeMessageOut)
def send_message(
    payload: RealLifeMessageIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = send_real_life_message(
        db,
        user,
        session_id=payload.session_id,
        message=payload.message,
        response_time_seconds=payload.response_time_seconds,
    )
    return RealLifeMessageOut(**data)
