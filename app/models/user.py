from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.reservation import Reservation


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    slack_user_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    team_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation",
        back_populates="user",
    )
