from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, get_current_user
from app.models.user import User, PlanEnum
from app.models.language import Language
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def validate_language_code(db: Session, code: str | None) -> None:
    if code is None:
        return
    exists = db.query(Language.iso_code).filter(Language.iso_code == code).first()
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid language code",
        )


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=password_hash,
        plan=PlanEnum.FREE,
        level=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me")
def me(current=Depends(get_current_user)):
    return current


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.plan is not None:
        user.plan = PlanEnum(payload.plan)
    if payload.level is not None:
        user.level = payload.level
    if payload.timezone is not None:
        user.timezone = payload.timezone

    validate_language_code(db, payload.target_language_code)
    validate_language_code(db, payload.base_language_code)

    if payload.target_language_code is not None:
        user.target_language_code = payload.target_language_code
    if payload.base_language_code is not None:
        user.base_language_code = payload.base_language_code

    db.commit()
    db.refresh(user)
    return user
