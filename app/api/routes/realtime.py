from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.realtime import (
    RealtimeIceServerOut,
    RealtimeSessionSignalIn,
    RealtimeSessionSignalOut,
    RealtimeSessionStartIn,
    RealtimeSessionStartOut,
    RealtimeSessionStopOut,
)

router = APIRouter(prefix="/realtime", tags=["realtime"])

_SESSION_TTL_MINUTES = 30
_sessions: dict[str, dict] = {}


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _cleanup_expired_sessions() -> None:
    now = _now_utc()
    expired = [sid for sid, row in _sessions.items() if row.get("expires_at") and row["expires_at"] < now]
    for sid in expired:
        _sessions.pop(sid, None)


def _get_owned_session(session_id: str, user: User) -> dict:
    _cleanup_expired_sessions()
    row = _sessions.get(session_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Realtime session not found")
    if row["user_id"] != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Realtime session does not belong to user")
    return row


@router.post("/sessions/start", response_model=RealtimeSessionStartOut)
def start_realtime_session(payload: RealtimeSessionStartIn, user: User = Depends(get_current_user)):
    _cleanup_expired_sessions()
    now = _now_utc()
    expires_at = now + timedelta(minutes=_SESSION_TTL_MINUTES)
    session_id = uuid4().hex

    _sessions[session_id] = {
        "session_id": session_id,
        "user_id": user.id,
        "mentor_id": payload.mentor_id,
        "mode": payload.mode,
        "status": "created",
        "created_at": now,
        "expires_at": expires_at,
        "signals": [],
    }

    # STUN baseline; TURN can be injected in future iterations.
    ice_servers = [RealtimeIceServerOut(urls=["stun:stun.l.google.com:19302"])]

    return RealtimeSessionStartOut(
        session_id=session_id,
        status="created",
        created_at=now,
        expires_at=expires_at,
        signaling_path=f"/realtime/sessions/{session_id}/signal",
        ice_servers=ice_servers,
        beta=True,
    )


@router.post("/sessions/{session_id}/signal", response_model=RealtimeSessionSignalOut)
def signal_realtime_session(
    session_id: str,
    payload: RealtimeSessionSignalIn,
    user: User = Depends(get_current_user),
):
    row = _get_owned_session(session_id, user)
    if row["status"] == "stopped":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Realtime session already stopped")

    row["signals"].append(
        {
            "signal_type": payload.signal_type,
            "payload": payload.payload,
            "created_at": _now_utc(),
        }
    )
    row["status"] = "negotiating"
    return RealtimeSessionSignalOut(session_id=session_id, accepted=True, status=row["status"])


@router.post("/sessions/{session_id}/stop", response_model=RealtimeSessionStopOut)
def stop_realtime_session(session_id: str, user: User = Depends(get_current_user)):
    row = _get_owned_session(session_id, user)
    row["status"] = "stopped"
    ended_at = _now_utc()
    row["ended_at"] = ended_at
    return RealtimeSessionStopOut(session_id=session_id, status="stopped", ended_at=ended_at)
