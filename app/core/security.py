from datetime import datetime, timedelta
import hashlib

from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import settings
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
from fastapi import Depends
from app.core.security import oauth2_scheme

def get_current_user(token: str = Depends(oauth2_scheme)):
    return token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=True)


def _prepare_password(password: str, allow_empty: bool = False) -> str:
    if password is None:
        raise ValueError("Password must not be empty.")

    if password == "":
        if allow_empty:
            return ""
        raise ValueError("Password must not be empty.")

    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        # bcrypt only handles 72 bytes; pre-hash to keep deterministic verification.
        return hashlib.sha256(password_bytes).hexdigest()
    return password


def hash_password(password: str) -> str:
    prepared = _prepare_password(password, allow_empty=False)
    return pwd_context.hash(prepared)


def verify_password(password: str, password_hash: str) -> bool:
    prepared = _prepare_password(password, allow_empty=True)
    if prepared == "":
        return False
    return pwd_context.verify(prepared, password_hash)


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_exp_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    subject = payload.get("sub")
    if not subject:
        raise JWTError("Invalid token")
    return str(subject)
