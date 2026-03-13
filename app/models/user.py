from sqlalchemy import String, Integer, Enum, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import enum


class PlanEnum(str, enum.Enum):
    FREE = "FREE"
    PRO = "PRO"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[PlanEnum] = mapped_column(Enum(PlanEnum), nullable=False, default=PlanEnum.FREE)
    xp_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    target_language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="America/Sao_Paulo")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subscription_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_language_code: Mapped[str | None] = mapped_column(
        ForeignKey("languages.iso_code"),
        nullable=True,
    )
    base_language_code: Mapped[str | None] = mapped_column(
        ForeignKey("languages.iso_code"),
        nullable=True,
    )

    @property
    def language(self) -> str | None:
        return self.target_language or self.target_language_code

    @language.setter
    def language(self, value: str | None) -> None:
        self.target_language = value
        self.target_language_code = value
