from typing import Iterable
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User


PUBLIC_PATHS: set[str] = {
    "/auth/login",
    "/users",
    "/docs",
    "/openapi.json",
    "/redoc",
}

FEATURE_RULES: dict[str, Iterable[str]] = {
    "/features/writing": ["FREE", "PRO"],
    "/features/speaking": ["PRO"],
    "/features/dialect": ["PRO"],
    "/features/fillers": ["PRO"],
    "/features/ads": ["FREE"],
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        if not path.startswith("/features"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()
        finally:
            db.close()

        if not user:
            return JSONResponse(status_code=401, content={"detail": "User not found"})

        allowed_plans = FEATURE_RULES.get(path)
        if allowed_plans is not None and user.plan.value not in allowed_plans:
            return JSONResponse(status_code=403, content={"detail": "Plan not allowed"})

        request.state.user = user
        return await call_next(request)
