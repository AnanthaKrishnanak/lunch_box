from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, UniqueConstraint
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ReservationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Reservation(Base, TimestampMixin):
    __tablename__ = "reservations"
    __table_args__ = (
        UniqueConstraint(
            "slack_user_id",
            "reservation_date",
            name="uq_reservation_user_date",
        ),
        Index(
            "ix_reservations_date_status_created_at",
            "reservation_date",
            "status",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reservation_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    status: Mapped[ReservationStatus] = mapped_column(
        SQLEnum(ReservationStatus),
        default=ReservationStatus.PENDING,
        nullable=False,
    )
    slack_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.slack_user_id"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="reservations")
