from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DailyMissionProgress(Base):
    __tablename__ = "daily_mission_progress"
    __table_args__ = (UniqueConstraint("user_id", "day_date", name="uq_daily_mission_user_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    day_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    completed_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bonus_xp_awarded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
