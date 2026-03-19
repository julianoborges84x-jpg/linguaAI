from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.daily_challenge import (
    DailyChallengeOut,
    DailyChallengeStartOut,
    DailyChallengeSubmitIn,
    DailyChallengeSubmitOut,
)
from app.services.daily_challenge_service import get_daily_challenge, start_daily_challenge, submit_daily_challenge

router = APIRouter(prefix="/daily-challenge", tags=["daily-challenge"])


@router.get("", response_model=DailyChallengeOut)
def daily_challenge(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return DailyChallengeOut(**get_daily_challenge(db, user))


@router.post("/start", response_model=DailyChallengeStartOut)
def daily_challenge_start(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return DailyChallengeStartOut(**start_daily_challenge(db, user))


@router.post("/submit", response_model=DailyChallengeSubmitOut)
def daily_challenge_submit(
    payload: DailyChallengeSubmitIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return DailyChallengeSubmitOut(**submit_daily_challenge(db, user, payload.challenge_id))
