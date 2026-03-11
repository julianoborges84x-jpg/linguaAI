from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.daily_message import DailyMessageOut
from app.services.daily_messages import get_or_create_daily_message, today_for_timezone
from app.services import progress_service

router = APIRouter(prefix="/daily-message", tags=["daily-message"])


@router.get("/today", response_model=DailyMessageOut)
def get_today_message(db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        today = today_for_timezone(user.timezone)
        msg = get_or_create_daily_message(db, user.id, today)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return msg


@router.get("/streak")
def get_streak(db: Session = Depends(get_db), user=Depends(get_current_user)):
    today = progress_service.today_for_user(user)
    return {"streak": progress_service.calculate_streak(db, user.id, today)}
