from datetime import date, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from app.utils.reservation import (
    get_next_reservation_date,
    get_next_reservation_dates_for_a_week,
    get_next_working_day,
)
from tests.factories import make_holiday

IST = ZoneInfo("Asia/Kolkata")


class TestGetNextWorkingDay:
    def test_weekday_passthrough(self):
        wednesday = date(2026, 7, 22)
        assert get_next_working_day(wednesday, set()) == wednesday

    def test_skips_saturday_and_sunday(self):
        saturday = date(2026, 7, 25)
        assert get_next_working_day(saturday, set()) == date(2026, 7, 27)

    def test_skips_holiday(self):
        wednesday = date(2026, 7, 22)
        holidays = {wednesday}
        assert get_next_working_day(wednesday, holidays) == date(2026, 7, 23)

    def test_skips_weekend_then_holiday(self):
        saturday = date(2026, 7, 25)
        holidays = {date(2026, 7, 27)}  # Monday
        assert get_next_working_day(saturday, holidays) == date(2026, 7, 28)


class TestGetNextReservationDate:
    def test_before_cutoff_returns_today(self, settings, wednesday_before_cutoff):
        with patch(
            "app.utils.reservation.now",
            return_value=wednesday_before_cutoff,
        ):
            assert get_next_reservation_date(settings, []) == date(2026, 7, 22)

    def test_after_cutoff_returns_next_working_day(
        self, settings, wednesday_after_cutoff
    ):
        with patch(
            "app.utils.reservation.now",
            return_value=wednesday_after_cutoff,
        ):
            assert get_next_reservation_date(settings, []) == date(2026, 7, 23)

    def test_weekend_returns_next_monday(self, settings, saturday):
        with patch("app.utils.reservation.now", return_value=saturday):
            assert get_next_reservation_date(settings, []) == date(2026, 7, 27)

    def test_holiday_returns_next_working_day(
        self, settings, wednesday_before_cutoff, holiday_on_wednesday
    ):
        with patch(
            "app.utils.reservation.now",
            return_value=wednesday_before_cutoff,
        ):
            assert get_next_reservation_date(settings, holiday_on_wednesday) == date(
                2026, 7, 23
            )

    def test_friday_after_cutoff_returns_monday(self, settings):
        friday_after_cutoff = datetime(2026, 7, 24, 11, 0, tzinfo=IST)
        with patch("app.utils.reservation.now", return_value=friday_after_cutoff):
            assert get_next_reservation_date(settings, []) == date(2026, 7, 27)


class TestGetNextReservationDatesForAWeek:
    def test_midweek_before_rollover_returns_remaining_days(
        self, settings, wednesday_before_cutoff
    ):
        with patch(
            "app.utils.reservation.now",
            return_value=wednesday_before_cutoff,
        ):
            assert get_next_reservation_dates_for_a_week(settings, []) == [
                date(2026, 7, 22),
                date(2026, 7, 23),
                date(2026, 7, 24),
            ]

    def test_after_rollover_returns_next_monday_to_friday(
        self, settings, wednesday_after_rollover
    ):
        with patch(
            "app.utils.reservation.now",
            return_value=wednesday_after_rollover,
        ):
            assert get_next_reservation_dates_for_a_week(settings, []) == [
                date(2026, 7, 27),
                date(2026, 7, 28),
                date(2026, 7, 29),
                date(2026, 7, 30),
                date(2026, 7, 31),
            ]

    def test_weekend_returns_next_week(self, settings, saturday):
        with patch("app.utils.reservation.now", return_value=saturday):
            assert get_next_reservation_dates_for_a_week(settings, []) == [
                date(2026, 7, 27),
                date(2026, 7, 28),
                date(2026, 7, 29),
                date(2026, 7, 30),
                date(2026, 7, 31),
            ]

    def test_holidays_are_dropped(self, settings, wednesday_before_cutoff):
        holidays = [make_holiday(date(2026, 7, 23), name="Midweek Holiday")]
        with patch(
            "app.utils.reservation.now",
            return_value=wednesday_before_cutoff,
        ):
            assert get_next_reservation_dates_for_a_week(settings, holidays) == [
                date(2026, 7, 22),
                date(2026, 7, 24),
            ]

    def test_monday_before_rollover_returns_full_week(self, settings):
        monday = datetime(2026, 7, 27, 9, 0, tzinfo=IST)
        with patch("app.utils.reservation.now", return_value=monday):
            assert get_next_reservation_dates_for_a_week(settings, []) == [
                date(2026, 7, 27),
                date(2026, 7, 28),
                date(2026, 7, 29),
                date(2026, 7, 30),
                date(2026, 7, 31),
            ]
