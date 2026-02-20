from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.motivation import MotivationEventIn, MotivationOut
from app.services.motivation import (
    seed_quotes_if_empty,
    pick_quote,
    record_event,
    has_streak_5_days,
    already_rewarded_today,
)

router = APIRouter(prefix="/motivation", tags=["motivation"])


@router.post("/event", response_model=MotivationOut)
def motivation_event(payload: MotivationEventIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    seed_quotes_if_empty(db)

    if payload.type == "level_up":
        if payload.new_level is None:
            raise HTTPException(status_code=422, detail="new_level is required for level_up")
        if payload.new_level <= user.level:
            return MotivationOut()
        user.level = payload.new_level
        db.commit()
        quote = pick_quote(db, user.id, "level_up")
        record_event(db, user.id, quote.id, "level_up")
        return MotivationOut(quote=quote.text, category=quote.category)

    if payload.type == "exercise_completed":
        quote = pick_quote(db, user.id, "exercise")
        record_event(db, user.id, quote.id, "exercise")
        return MotivationOut(quote=quote.text, category=quote.category)

    if payload.type == "streak_check":
        today = date.today()
        if already_rewarded_today(db, user.id, "streak_5days", today):
            return MotivationOut()
        if not has_streak_5_days(db, user.id, today):
            return MotivationOut()
        quote = pick_quote(db, user.id, "streak")
        record_event(db, user.id, quote.id, "streak_5days")
        return MotivationOut(quote=quote.text, category=quote.category)

    return MotivationOut()
