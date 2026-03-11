from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.session import SessionFinishIn, SessionFinishOut, SessionStartIn, SessionStartOut
from app.services.session_service import finish_session, start_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionStartOut)
def start(payload: SessionStartIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    session = start_session(db, user, payload.mode, payload.topic_id)
    return SessionStartOut(session_id=session.id)


@router.post("/{session_id}/finish", response_model=SessionFinishOut)
def finish(
    session_id: int,
    payload: SessionFinishIn | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    interactions_count = payload.interactions_count if payload is not None else None
    session = finish_session(db, user, session_id, interactions_count)
    return SessionFinishOut(
        session_id=session.id,
        xp_earned=session.xp_earned,
        interactions_count=session.interactions_count,
        finished_at=session.finished_at,
    )
