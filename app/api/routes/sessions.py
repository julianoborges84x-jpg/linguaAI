from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.session import SessionFinishIn, SessionFinishOut, SessionStartIn, SessionStartOut, SessionTopicOut
from app.services.session_service import finish_session, start_session
from app.services.topic_service import ensure_default_topics

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionStartOut)
def start(payload: SessionStartIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    session = start_session(db, user, payload.mode, payload.topic_id)
    return SessionStartOut(session_id=session.id)


@router.get("/topics", response_model=list[SessionTopicOut])
def list_session_topics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ensure_default_topics(db)


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
