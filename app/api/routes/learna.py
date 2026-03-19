from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_pro_user
from app.models.message import Message
from app.models.progress import Progress
from app.models.topic import Topic
from app.models.user import User
from app.models.vocabulary import Vocabulary
from app.schemas.learna import (
    ChatIn,
    ChatOut,
    MessageOut,
    ProgressOut,
    ProgressUpdate,
    TopicOut,
    VocabularyOut,
)
from app.schemas.session import ProgressSummaryOut
from app.services.chat_ai import generate_correction
from app.services.progress_service import build_progress_summary
from app.services.topic_service import ensure_default_topics

router = APIRouter(prefix="", tags=["learna"])

DEFAULT_VOCABULARY = [
    ("appointment", "A time arranged for a meeting.", "I have a dentist appointment at 3 PM."),
    ("bargain", "A good deal for a lower price.", "This jacket is a bargain today."),
    ("commute", "Travel between home and work.", "My commute takes 30 minutes."),
]


def ensure_seed_data(db: Session) -> None:
    ensure_default_topics(db)

    if db.query(Vocabulary.id).count() == 0:
        for word, definition, example in DEFAULT_VOCABULARY:
            db.add(Vocabulary(word=word, definition=definition, example=example))

    db.commit()


def get_or_create_progress(db: Session, user_id: int) -> Progress:
    progress = db.query(Progress).filter(Progress.user_id == user_id).first()
    if progress:
        return progress

    progress = Progress(user_id=user_id, streak=0, hours_spoken=0.0, words_learned=0)
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


@router.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, db: Session = Depends(get_db), user: User = Depends(require_pro_user)):
    if not payload.message.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Message is required")

    result = generate_correction(payload.message)
    db.add(
        Message(
            user_id=user.id,
            message=payload.message,
            corrected=result["corrected_text"],
            explanation=result["explanation"],
        )
    )
    progress = get_or_create_progress(db, user.id)
    progress.words_learned += max(1, len(result["corrected_text"].split()) // 2)
    db.commit()

    return ChatOut(
        correction=result["correction"],
        explanation=result["explanation"],
        corrected_text=result["corrected_text"],
    )


@router.get("/topics", response_model=list[TopicOut])
def list_topics(db: Session = Depends(get_db), user: User = Depends(require_pro_user)):
    ensure_seed_data(db)
    return db.query(Topic).order_by(Topic.name.asc()).all()


@router.get("/history", response_model=list[MessageOut])
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Message)
        .filter(Message.user_id == user.id)
        .order_by(Message.created_at.desc())
        .limit(100)
        .all()
    )


@router.get("/vocabulary", response_model=list[VocabularyOut])
def vocabulary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ensure_seed_data(db)
    return db.query(Vocabulary).order_by(Vocabulary.word.asc()).all()


@router.get("/progress", response_model=ProgressOut)
def progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = get_or_create_progress(db, user.id)
    return ProgressOut(
        streak=record.streak,
        hours_spoken=record.hours_spoken,
        words_learned=record.words_learned,
    )


@router.patch("/progress", response_model=ProgressOut)
def update_progress(payload: ProgressUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = get_or_create_progress(db, user.id)
    if payload.streak is not None:
        record.streak = max(0, payload.streak)
    if payload.hours_spoken is not None:
        record.hours_spoken = max(0.0, payload.hours_spoken)
    if payload.words_learned is not None:
        record.words_learned = max(0, payload.words_learned)

    db.commit()
    db.refresh(record)
    return ProgressOut(
        streak=record.streak,
        hours_spoken=record.hours_spoken,
        words_learned=record.words_learned,
    )


@router.get("/progress/summary", response_model=ProgressSummaryOut)
def progress_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return build_progress_summary(db, user)
