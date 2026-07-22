from datetime import date, timedelta

from app.core.time import now
from app.models.holiday import Holiday
from app.models.system_settings import SystemSettings


def get_next_working_day(
    start_date: date,
    holiday_dates: set[date],
) -> date:
    """Return the next working day, skipping weekends and holidays."""
    while start_date.weekday() >= 5 or start_date in holiday_dates:
        start_date += timedelta(days=1)

    return start_date


def get_next_reservation_date(
    system_settings: SystemSettings,
    holidays: list[Holiday],
) -> date:
    """Return the date for which the next reservation should be created."""
    current_datetime = now()
    current_date = current_datetime.date()

    holiday_dates: set[date] = {holiday.date for holiday in holidays}

    # Reservations cannot be made for weekends.
    if current_datetime.weekday() >= 5:
        return get_next_working_day(current_date, holiday_dates)

    # Reservations cannot be made for holidays.
    if current_date in holiday_dates:
        return get_next_working_day(current_date, holiday_dates)

    # Before the day rollover time, the reservation is for the current working day.
    if current_datetime.time() < system_settings.day_rollover_time:
        return current_date

    # After the day rollover time, move to the next available working day.
    return get_next_working_day(
        current_date + timedelta(days=1),
        holiday_dates,
    )


def get_next_reservation_dates_for_a_week(
    system_settings: SystemSettings,
    holidays: list[Holiday],
) -> list[date]:
    """Return the remaining reservable working days for the current or next week."""

    current_datetime = now()
    today = current_datetime.date()

    holiday_dates = {holiday.date for holiday in holidays}

    is_weekend = current_datetime.weekday() >= 5
    has_passed_rollover_time = (
        current_datetime.time() >= system_settings.day_rollover_time
    )

    if is_weekend:
        days_until_monday = 7 - today.weekday()
        first_reservation_date = today + timedelta(days=days_until_monday)
    elif has_passed_rollover_time:
        first_reservation_date = today + timedelta(days=1)
    else:
        first_reservation_date = today

    last_reservation_date = first_reservation_date + timedelta(
        days=4 - first_reservation_date.weekday()
    )

    reservation_dates: list[date] = []
    reservation_date = first_reservation_date

    while reservation_date <= last_reservation_date:
        if reservation_date not in holiday_dates:
            reservation_dates.append(reservation_date)

        reservation_date += timedelta(days=1)

    return reservation_dates
