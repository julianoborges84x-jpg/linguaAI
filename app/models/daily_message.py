from sqlalchemy import Integer, Date, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from app.core.database import Base


class DailyMessage(Base):
    __tablename__ = "daily_messages"
    __table_args__ = (
        UniqueConstraint("user_id", "day", name="uq_daily_messages_user_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    day: Mapped[date] = mapped_column(Date, nullable=False)
    passage_id: Mapped[str] = mapped_column(String(64), nullable=False)
    reference: Mapped[str] = mapped_column(String(120), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
