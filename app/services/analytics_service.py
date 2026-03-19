from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.analytics_event import AnalyticsEvent


def track_event(db: Session, event_type: str, user_id: int | None = None, payload: dict[str, Any] | None = None) -> AnalyticsEvent:
    event = AnalyticsEvent(
        user_id=user_id,
        event_type=event_type.strip().lower(),
        payload_json=json.dumps(payload or {}, ensure_ascii=True),
    )
    db.add(event)
    return event
