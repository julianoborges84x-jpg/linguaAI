import json
import random
from pathlib import Path
from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from sqlalchemy.orm import Session
from app.models.daily_message import DailyMessage

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "bible_passages.json"


def load_passages() -> list[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("passages", [])


def get_or_create_daily_message(db: Session, user_id: int, day: date) -> DailyMessage:
    existing = (
        db.query(DailyMessage)
        .filter(DailyMessage.user_id == user_id, DailyMessage.day == day)
        .first()
    )
    if existing:
        return existing

    passages = load_passages()
    if not passages:
        raise ValueError("No passages available")

    used_ids = {
        p for (p,) in db.query(DailyMessage.passage_id)
        .filter(DailyMessage.user_id == user_id)
        .all()
    }

    candidates = [p for p in passages if p.get("id") not in used_ids]
    if not candidates:
        candidates = passages

    chosen = random.choice(candidates)

    msg = DailyMessage(
        user_id=user_id,
        day=day,
        passage_id=str(chosen.get("id")),
        reference=str(chosen.get("reference", "")),
        text=str(chosen.get("text", "")),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def today_for_timezone(tz_name: str) -> date:
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    return datetime.now(tz).date()
