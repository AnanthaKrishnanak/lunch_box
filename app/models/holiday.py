from datetime import date as type_date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import Base, TimestampMixin


class Holiday(Base, TimestampMixin):
    __tablename__ = "holidays"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[type_date] = mapped_column(
        Date,
        nullable=False,
        unique=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
