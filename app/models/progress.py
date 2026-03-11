from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Progress(Base):
    __tablename__ = "progress"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_spoken: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    words_learned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
