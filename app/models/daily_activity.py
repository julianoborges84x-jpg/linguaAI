from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DailyActivity(Base):
    __tablename__ = "daily_activities"
    __table_args__ = (UniqueConstraint("user_id", "day_date", name="uq_daily_activity_user_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    day_date: Mapped[date] = mapped_column(Date, nullable=False)
