from datetime import time

from sqlalchemy import Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import Base, TimestampMixin


class SystemSettings(Base, TimestampMixin):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    cutoff_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
    day_rollover_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
