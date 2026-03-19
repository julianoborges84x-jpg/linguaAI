from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.referral import ReferralApplyIn, ReferralApplyOut, ReferralMeOut, ReferralStatsOut
from app.services.referral_service import apply_referral, referral_me, referral_stats

router = APIRouter(prefix="/referral", tags=["referral"])


@router.get("/me", response_model=ReferralMeOut)
def me(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ReferralMeOut(**referral_me(db, user))


@router.post("/apply", response_model=ReferralApplyOut)
def apply(payload: ReferralApplyIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ReferralApplyOut(**apply_referral(db, user, payload.referral_code))


@router.get("/stats", response_model=ReferralStatsOut)
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ReferralStatsOut(**referral_stats(db, user))
