from sqlalchemy.orm import Session

from app.models.topic import Topic

DEFAULT_TOPICS = [
    ("jobs", "career"),
    ("travel", "lifestyle"),
    ("dating", "social"),
    ("shopping", "daily"),
]


def ensure_default_topics(db: Session) -> list[Topic]:
    if db.query(Topic.id).count() == 0:
        for name, category in DEFAULT_TOPICS:
            db.add(Topic(name=name, category=category))
        db.commit()
    return db.query(Topic).order_by(Topic.id.asc()).all()


def get_first_topic_id(db: Session) -> int | None:
    topics = ensure_default_topics(db)
    if not topics:
        return None
    return topics[0].id


def topic_exists(db: Session, topic_id: int) -> bool:
    return db.query(Topic.id).filter(Topic.id == topic_id).first() is not None

