import re
import secrets
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import hash_password
from app.models.language import Language
from app.models.user import PlanEnum, User
from app.schemas.user import (
    UserCreate,
    UserOut,
    UserPreferencesOut,
    UserPreferencesUpdate,
    UserUpdate,
)
from app.schemas.user_preferences import UserPreferencesUpdate as OnboardingPreferencesUpdate
from app.services.analytics_service import track_event
from app.services.email_service import send_verification_email
from app.services.growth_service import apply_referral_if_valid, ensure_referral_code

router = APIRouter(prefix="/users", tags=["users"])
legacy_router = APIRouter(prefix="/user", tags=["users-legacy"])
LANGUAGE_CODE_PATTERN = re.compile(r"^[a-z]{2,3}$")


def validate_language_code(code: str | None) -> str | None:
    if code is None:
        return None

    normalized = code.strip().lower()
    if not normalized:
        return None

    if not LANGUAGE_CODE_PATTERN.match(normalized):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid language code.",
        )
    return normalized


def validate_timezone(tz_name: str | None) -> str | None:
    if tz_name is None:
        return None

    normalized = tz_name.strip()
    if not normalized:
        return None

    try:
        ZoneInfo(normalized)
    except ZoneInfoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid timezone. Use IANA timezone (e.g. 'America/Sao_Paulo').",
        )
    return normalized


def ensure_language_exists(db: Session, code: str) -> None:
    existing = db.query(Language.iso_code).filter(Language.iso_code == code).first()
    if existing:
        return

    db.add(
        Language(
            iso_code=code,
            name=code.upper(),
            region="Unknown",
            family="Unknown",
        )
    )


def apply_user_update(user: User, payload: UserUpdate, db: Session) -> None:
    if payload.plan is not None:
        user.plan = PlanEnum(payload.plan)

    if payload.level is not None:
        user.level = payload.level

    if payload.timezone is not None:
        user.timezone = validate_timezone(payload.timezone) or "America/Sao_Paulo"

    effective_target = payload.target_language
    if effective_target is None:
        effective_target = payload.target_language_code
    if effective_target is None:
        effective_target = payload.language

    target_code = validate_language_code(effective_target)
    base_code = validate_language_code(payload.base_language_code)

    if target_code:
        ensure_language_exists(db, target_code)
    if base_code:
        ensure_language_exists(db, base_code)

    if effective_target is not None:
        user.target_language = target_code
        user.target_language_code = target_code

    if payload.base_language_code is not None:
        user.base_language_code = base_code


def _normalize_with_length(value: str, min_len: int, max_len: int, field_name: str) -> str:
    normalized = value.strip()
    if len(normalized) < min_len or len(normalized) > max_len:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_name} must be between {min_len} and {max_len} characters.",
        )
    return normalized


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    password_hash = hash_password(payload.password)

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=password_hash,
        is_verified=False,
        verification_token=secrets.token_urlsafe(32),
    )

    db.add(user)
    db.flush()
    ensure_referral_code(db, user)
    apply_referral_if_valid(db, user, payload.referral_code)
    track_event(db, "user_registered", user_id=user.id, payload={"referred_by_user_id": user.referred_by_user_id})
    if user.referred_by_user_id:
        track_event(
            db,
            "referral_converted",
            user_id=user.referred_by_user_id,
            payload={"new_user_id": user.id},
        )
    db.commit()
    db.refresh(user)

    send_verification_email(user.email, user.verification_token)

    return user


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido.",
        )

    user.is_verified = True
    user.verification_token = None

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "E-mail verificado com sucesso."}


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current


@legacy_router.get("/me", response_model=UserOut, include_in_schema=False)
def me_legacy(current: User = Depends(get_current_user)):
    return me(current)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: OnboardingPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    normalized_timezone = payload.timezone.strip()
    if not normalized_timezone:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="timezone cannot be empty.",
        )

    ensure_language_exists(db, payload.target_language)
    current_user.target_language = payload.target_language
    current_user.target_language_code = payload.target_language
    current_user.timezone = normalized_timezone
    current_user.onboarding_completed = True

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user update payload",
        )

    db.refresh(current_user)
    return current_user


@legacy_router.patch("/me", response_model=UserOut, include_in_schema=False)
def update_me_legacy(
    payload: OnboardingPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_me(payload, db, current_user)


@router.patch("/me/onboarding", response_model=UserOut)
def complete_onboarding(
    payload: OnboardingPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_me(payload, db, current_user)


@legacy_router.patch("/me/onboarding", response_model=UserOut, include_in_schema=False)
def complete_onboarding_legacy(
    payload: OnboardingPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_me(payload, db, current_user)


@router.get("/preferences", response_model=UserPreferencesOut)
def get_preferences(current_user: User = Depends(get_current_user)):
    return UserPreferencesOut(
        target_language_code=current_user.target_language_code,
        timezone=current_user.timezone,
        onboarding_completed=current_user.onboarding_completed,
    )


@router.put("/preferences", response_model=UserPreferencesOut)
def update_preferences(
    payload: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.target_language_code = _normalize_with_length(
        payload.target_language_code.lower(),
        2,
        8,
        "target_language_code",
    )
    current_user.timezone = _normalize_with_length(
        payload.timezone,
        1,
        64,
        "timezone",
    )
    current_user.onboarding_completed = True

    db.commit()
    db.refresh(current_user)

    return UserPreferencesOut(
        target_language_code=current_user.target_language_code,
        timezone=current_user.timezone,
        onboarding_completed=current_user.onboarding_completed,
    )


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    apply_user_update(user, payload, db)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user update payload",
        )

    db.refresh(user)
    return user

