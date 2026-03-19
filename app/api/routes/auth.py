from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode
import secrets

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import TokenOut
from app.schemas.user import UserOut
from app.services.analytics_service import track_event
from app.services.growth_service import ensure_referral_code

router = APIRouter(prefix="/auth", tags=["auth"])


class OAuthCodeIn(BaseModel):
    code: str = Field(min_length=1)
    state: str = Field(min_length=1)


class OAuthStartOut(BaseModel):
    provider: str
    enabled: bool
    authorization_url: str | None = None


class OAuthLoginOut(TokenOut):
    user: UserOut


def _oauth_redirect_uri(provider: str) -> str:
    return f"{settings.frontend_url.rstrip('/')}/login/oauth/{provider}/callback"


def _encode_state(provider: str) -> str:
    payload = {
        "provider": provider,
        "nonce": secrets.token_urlsafe(12),
        "exp": datetime.now(UTC) + timedelta(minutes=10),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _validate_state(provider: str, state: str) -> None:
    try:
        payload = jwt.decode(state, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state invalido ou expirado.") from exc

    token_provider = str(payload.get("provider") or "").strip().lower()
    if token_provider != provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state nao corresponde ao provedor.")


def _oauth_enabled(provider: str) -> bool:
    if provider == "google":
        return bool(settings.oauth_google_client_id and settings.oauth_google_client_secret)
    if provider == "apple":
        return bool(
            settings.oauth_apple_client_id
            and settings.oauth_apple_team_id
            and settings.oauth_apple_key_id
            and settings.oauth_apple_private_key
        )
    return False


def _build_apple_client_secret() -> str:
    raw_key = settings.oauth_apple_private_key.strip()
    private_key = raw_key.replace("\\n", "\n")
    now = datetime.now(UTC)
    payload = {
        "iss": settings.oauth_apple_team_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=180)).timestamp()),
        "aud": "https://appleid.apple.com",
        "sub": settings.oauth_apple_client_id,
    }
    headers = {"kid": settings.oauth_apple_key_id}
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)


def _exchange_google_code(code: str) -> tuple[str | None, str | None, str | None]:
    token_payload = {
        "code": code,
        "client_id": settings.oauth_google_client_id,
        "client_secret": settings.oauth_google_client_secret,
        "redirect_uri": _oauth_redirect_uri("google"),
        "grant_type": "authorization_code",
    }

    with httpx.Client(timeout=15.0) as client:
        token_resp = client.post("https://oauth2.googleapis.com/token", data=token_payload)
        if token_resp.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Falha no login Google. Tente novamente.")
        token_data = token_resp.json()
        access_token = token_data.get("access_token", "")

        if not access_token:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Google nao retornou access token.")

        profile_resp = client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if profile_resp.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Falha ao obter perfil do Google.")
        profile = profile_resp.json()

    email = (profile.get("email") or "").strip().lower() or None
    name = (profile.get("name") or "").strip() or None
    subject = (profile.get("sub") or "").strip() or None
    return email, name, subject


def _exchange_apple_code(code: str) -> tuple[str | None, str | None, str | None]:
    client_secret = _build_apple_client_secret()
    token_payload = {
        "client_id": settings.oauth_apple_client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": _oauth_redirect_uri("apple"),
    }

    with httpx.Client(timeout=15.0) as client:
        token_resp = client.post("https://appleid.apple.com/auth/token", data=token_payload)
        if token_resp.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Falha no login Apple. Tente novamente.")
        token_data = token_resp.json()

    id_token = str(token_data.get("id_token") or "")
    if not id_token:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Apple nao retornou id_token.")

    claims = jwt.get_unverified_claims(id_token)
    email = (claims.get("email") or "").strip().lower() or None
    subject = (claims.get("sub") or "").strip() or None
    name = "Apple User"
    return email, name, subject


def _resolve_oauth_user(
    db: Session,
    provider: str,
    subject: str | None,
    email: str | None,
    name: str | None,
) -> tuple[User, bool]:
    user = None
    created = False

    if provider == "google" and subject:
        user = db.query(User).filter(User.google_sub == subject).first()
    elif provider == "apple" and subject:
        user = db.query(User).filter(User.apple_sub == subject).first()

    if not user and email:
        user = db.query(User).filter(User.email == email).first()

    if not user:
        if not email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Nao foi possivel criar conta social sem e-mail do provedor.",
            )
        user = User(
            name=(name or email.split("@")[0]).strip()[:120] or "LinguaAI User",
            email=email,
            password_hash=hash_password(secrets.token_urlsafe(24)),
            is_verified=True,
            verification_token=None,
        )
        if provider == "google":
            user.google_sub = subject
        if provider == "apple":
            user.apple_sub = subject
        db.add(user)
        db.flush()
        ensure_referral_code(db, user)
        created = True
    else:
        if provider == "google" and subject and not user.google_sub:
            user.google_sub = subject
        if provider == "apple" and subject and not user.apple_sub:
            user.apple_sub = subject
        if not user.is_verified:
            user.is_verified = True
            user.verification_token = None

    db.add(user)
    db.commit()
    db.refresh(user)
    return user, created


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(str(user.id))
    track_event(db, "login_success", user_id=user.id)
    db.commit()
    return TokenOut(access_token=token, token_type="bearer")


@router.get("/oauth/{provider}/start")
def oauth_start(provider: str):
    provider = provider.strip().lower()
    if provider not in {"google", "apple"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OAuth provider not supported.")

    if not _oauth_enabled(provider):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OAuth {provider.title()} nao configurado no servidor.",
        )

    state = _encode_state(provider)
    redirect_uri = _oauth_redirect_uri(provider)

    if provider == "google":
        params = {
            "client_id": settings.oauth_google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return RedirectResponse(url=url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    params = {
        "response_type": "code",
        "response_mode": "query",
        "client_id": settings.oauth_apple_client_id,
        "redirect_uri": redirect_uri,
        "scope": "name email",
        "state": state,
    }
    url = f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"
    return RedirectResponse(url=url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/oauth/providers", response_model=list[OAuthStartOut])
def oauth_providers_status():
    providers = ["google", "apple"]
    return [OAuthStartOut(provider=provider, enabled=_oauth_enabled(provider)) for provider in providers]


@router.post("/oauth/{provider}/callback", response_model=OAuthLoginOut)
def oauth_callback(provider: str, payload: OAuthCodeIn, db: Session = Depends(get_db)):
    provider = provider.strip().lower()
    if provider not in {"google", "apple"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OAuth provider not supported.")

    if not _oauth_enabled(provider):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OAuth {provider.title()} nao configurado no servidor.",
        )

    _validate_state(provider, payload.state)

    if provider == "google":
        email, name, subject = _exchange_google_code(payload.code)
    else:
        email, name, subject = _exchange_apple_code(payload.code)

    user, created = _resolve_oauth_user(db, provider, subject, email, name)
    token = create_access_token(str(user.id))

    track_event(db, f"oauth_{provider}_{'signup' if created else 'login'}", user_id=user.id)
    db.commit()

    return OAuthLoginOut(access_token=token, token_type="bearer", user=user)


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    user.is_verified = True
    user.verification_token = None

    db.commit()

    return {"message": "Email successfully verified"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
