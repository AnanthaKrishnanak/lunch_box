from datetime import date, time

from app.models.holiday import Holiday
from app.models.reservation import Reservation, ReservationStatus
from app.models.system_settings import SystemSettings


def make_system_settings(
    *,
    cutoff_time: time | None = None,
    day_rollover_time: time | None = None,
) -> SystemSettings:
    return SystemSettings(
        id=1,
        cutoff_time=cutoff_time or time(10, 0),
        day_rollover_time=day_rollover_time or time(15, 0),
    )


def make_holiday(
    holiday_date: date,
    *,
    name: str = "Holiday",
    holiday_id: int = 1,
) -> Holiday:
    return Holiday(id=holiday_id, date=holiday_date, name=name)


def make_reservation(
    *,
    slack_user_id: str = "U123",
    reservation_date: date,
    status: ReservationStatus = ReservationStatus.CONFIRMED,
    reservation_id: int = 1,
) -> Reservation:
    return Reservation(
        id=reservation_id,
        slack_user_id=slack_user_id,
        reservation_date=reservation_date,
        status=status,
    )
