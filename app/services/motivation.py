import json
import random
from pathlib import Path
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from app.models.motivational_quote import MotivationalQuote
from app.models.motivational_event import MotivationalEvent
from app.models.daily_message import DailyMessage

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "motivational_quotes.json"


def load_quotes() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("quotes", [])


def seed_quotes_if_empty(db: Session) -> None:
    if db.query(MotivationalQuote.id).first():
        return
    quotes = load_quotes()
    for q in quotes:
        text = str(q.get("text", "")).strip()
        category = str(q.get("category", "")).strip()
        if text and category:
            db.add(MotivationalQuote(text=text, category=category))
    db.commit()


def pick_quote(db: Session, user_id: int, category: str) -> MotivationalQuote:
    used = {
        qid for (qid,) in db.query(MotivationalEvent.quote_id)
        .filter(MotivationalEvent.user_id == user_id)
        .all()
    }

    candidates = (
        db.query(MotivationalQuote)
        .filter(MotivationalQuote.category == category)
        .all()
    )

    unused = [q for q in candidates if q.id not in used]
    if unused:
        return random.choice(unused)
    if candidates:
        return random.choice(candidates)
    raise ValueError("No motivational quotes available")


def record_event(db: Session, user_id: int, quote_id: int, reason: str) -> MotivationalEvent:
    evt = MotivationalEvent(user_id=user_id, quote_id=quote_id, reason=reason)
    db.add(evt)
    db.commit()
    db.refresh(evt)
    return evt


def has_streak_5_days(db: Session, user_id: int, today: date) -> bool:
    days = (
        db.query(DailyMessage.day)
        .filter(DailyMessage.user_id == user_id, DailyMessage.day <= today)
        .distinct()
        .order_by(DailyMessage.day.desc())
        .limit(5)
        .all()
    )
    if len(days) < 5:
        return False
    dates = [d for (d,) in days]
    expected = [today - timedelta(days=i) for i in range(5)]
    return dates == expected


def already_rewarded_today(db: Session, user_id: int, reason: str, today: date) -> bool:
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    return (
        db.query(MotivationalEvent.id)
        .filter(
            MotivationalEvent.user_id == user_id,
            MotivationalEvent.reason == reason,
            MotivationalEvent.created_at >= start,
            MotivationalEvent.created_at <= end,
        )
        .first()
        is not None
    )
