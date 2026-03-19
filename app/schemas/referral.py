from datetime import date

from pydantic import BaseModel


class ReferralMeOut(BaseModel):
    referral_code: str
    invite_link: str
    pro_access_until: date | None = None


class ReferralApplyIn(BaseModel):
    referral_code: str


class ReferralApplyOut(BaseModel):
    applied: bool
    referred_by: int | None = None
    xp_total: int
    level: int
    pro_access_until: date | None = None


class ReferralInvitedUserOut(BaseModel):
    user_id: int
    name: str
    email: str


class ReferralStatsOut(BaseModel):
    referral_count: int
    reward_xp_total: int
    pro_access_until: date | None = None
    invited_users: list[ReferralInvitedUserOut]
