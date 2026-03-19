from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from .config import settings

pwd_context = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError, VerificationError):
        return False


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_exp_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    subject = payload.get("sub")
    if not subject:
        raise JWTError("Invalid token")
    return str(subject)


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    resolved_token = (token or "").strip()
    if not resolved_token:
        auth_header = request.headers.get("Authorization", "")
        scheme, credentials = get_authorization_scheme_param(auth_header)
        if credentials and scheme.lower() in {"bearer", "token"}:
            resolved_token = credentials.strip()
        elif auth_header.strip() and " " not in auth_header.strip():
            resolved_token = auth_header.strip()

    if not resolved_token:
        resolved_token = request.headers.get("X-Access-Token", "").strip()

    if not resolved_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        user_id = decode_access_token(resolved_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    try:
        parsed_user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == parsed_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
