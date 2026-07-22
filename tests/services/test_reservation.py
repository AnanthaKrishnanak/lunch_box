from contextlib import ExitStack, contextmanager
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import BackgroundTasks

from app.core.exceptions import NotFoundError
from app.models.reservation import ReservationStatus
from app.repositories.reservation import ReservationRepository
from app.services.reservation import ReservationService
from app.tasks.notify import notify
from tests.factories import make_reservation


@pytest.fixture
def repo():
    return AsyncMock(spec=ReservationRepository)


@pytest.fixture
def background_tasks():
    return MagicMock(spec=BackgroundTasks)


@pytest.fixture
def service(repo, background_tasks):
    return ReservationService(repo, background_tasks)


@contextmanager
def _patch_clock_and_cache(
    settings,
    holidays,
    fixed_dt,
    *,
    next_reservation_date=None,
    week_dates=None,
):
    with ExitStack() as stack:
        stack.enter_context(
            patch(
                "app.core.cache.get_system_settings",
                AsyncMock(return_value=settings),
            )
        )
        stack.enter_context(
            patch(
                "app.core.cache.get_holidays",
                AsyncMock(return_value=holidays),
            )
        )
        stack.enter_context(
            patch("app.services.reservation.now", return_value=fixed_dt)
        )
        stack.enter_context(
            patch(
                "app.services.reservation.today",
                return_value=fixed_dt.date(),
            )
        )
        stack.enter_context(patch("app.utils.reservation.now", return_value=fixed_dt))
        if next_reservation_date is not None:
            stack.enter_context(
                patch(
                    "app.services.reservation.get_next_reservation_date",
                    return_value=next_reservation_date,
                )
            )
        if week_dates is not None:
            stack.enter_context(
                patch(
                    "app.services.reservation.get_next_reservation_dates_for_a_week",
                    return_value=week_dates,
                )
            )
        yield


class TestAddReservation:
    async def test_missing_settings_raises_not_found(
        self, service, wednesday_before_cutoff
    ):
        with (
            _patch_clock_and_cache(None, [], wednesday_before_cutoff),
            pytest.raises(NotFoundError),
        ):
            await service.add_reservation("U123")

    async def test_existing_pending_returns_waiting_list_message(
        self, service, repo, settings, wednesday_before_cutoff
    ):
        repo.get_reservation_by_date.return_value = make_reservation(
            reservation_date=date(2026, 7, 22),
            status=ReservationStatus.PENDING,
        )
        with _patch_clock_and_cache(settings, [], wednesday_before_cutoff):
            result = await service.add_reservation("U123")

        assert result.message == "You are already in the waiting list"
        repo.create.assert_not_awaited()

    async def test_existing_confirmed_returns_already_counted_message(
        self, service, repo, settings, wednesday_before_cutoff
    ):
        repo.get_reservation_by_date.return_value = make_reservation(
            reservation_date=date(2026, 7, 22),
            status=ReservationStatus.CONFIRMED,
        )
        with _patch_clock_and_cache(settings, [], wednesday_before_cutoff):
            result = await service.add_reservation("U123")

        assert result.message == "You have already given the food count, chill!"
        repo.create.assert_not_awaited()

    async def test_before_cutoff_creates_confirmed(
        self, service, repo, settings, wednesday_before_cutoff
    ):
        repo.get_reservation_by_date.return_value = None
        with _patch_clock_and_cache(settings, [], wednesday_before_cutoff):
            result = await service.add_reservation("U123")

        assert result.message == ("Successfully added the food count for 2026-07-22")
        created = repo.create.await_args.args[0]
        assert created.status == ReservationStatus.CONFIRMED
        assert created.reservation_date == date(2026, 7, 22)
        assert created.slack_user_id == "U123"
        repo.claim_cancelled_reservation.assert_not_awaited()

    async def test_after_rollover_uses_next_working_day(
        self, service, repo, settings, wednesday_after_rollover
    ):
        repo.get_reservation_by_date.return_value = None
        with _patch_clock_and_cache(settings, [], wednesday_after_rollover):
            result = await service.add_reservation("U123")

        assert result.message == ("Successfully added the food count for 2026-07-23")
        created = repo.create.await_args.args[0]
        assert created.status == ReservationStatus.CONFIRMED
        assert created.reservation_date == date(2026, 7, 23)
        # reservation_date != today, so claim path is skipped
        repo.claim_cancelled_reservation.assert_not_awaited()

    async def test_same_day_after_cutoff_claim_success_creates_confirmed(
        self, service, repo, settings, wednesday_after_cutoff
    ):
        repo.get_reservation_by_date.return_value = None
        repo.claim_cancelled_reservation.return_value = True

        with _patch_clock_and_cache(
            settings,
            [],
            wednesday_after_cutoff,
            next_reservation_date=date(2026, 7, 22),
        ):
            result = await service.add_reservation("U123")

        assert result.message == ("Successfully added the food count for 2026-07-22")
        created = repo.create.await_args.args[0]
        assert created.status == ReservationStatus.CONFIRMED
        repo.claim_cancelled_reservation.assert_awaited_once_with(
            reservation_date=date(2026, 7, 22),
        )

    async def test_same_day_after_cutoff_claim_fails_creates_pending(
        self, service, repo, settings, wednesday_after_cutoff
    ):
        repo.get_reservation_by_date.return_value = None
        repo.claim_cancelled_reservation.return_value = False

        with _patch_clock_and_cache(
            settings,
            [],
            wednesday_after_cutoff,
            next_reservation_date=date(2026, 7, 22),
        ):
            result = await service.add_reservation("U123")

        assert result.message == "You are added to the waiting list"
        created = repo.create.await_args.args[0]
        assert created.status == ReservationStatus.PENDING


class TestAddReservationForAWeek:
    async def test_all_dates_already_reserved(
        self, service, repo, settings, wednesday_before_cutoff
    ):
        existing = [
            make_reservation(
                reservation_date=d,
                reservation_id=i,
            )
            for i, d in enumerate(
                [date(2026, 7, 22), date(2026, 7, 23), date(2026, 7, 24)],
                start=1,
            )
        ]
        repo.get_reservations_by_dates.return_value = existing
        with _patch_clock_and_cache(settings, [], wednesday_before_cutoff):
            result = await service.add_reservation_for_a_week("U123")

        assert result.message == ("You have already given the food count for this week")
        repo.bulk_create.assert_not_awaited()

    async def test_no_days_available(
        self, service, repo, settings, wednesday_before_cutoff
    ):
        repo.get_reservations_by_dates.return_value = []
        with _patch_clock_and_cache(
            settings,
            [],
            wednesday_before_cutoff,
            week_dates=[],
        ):
            result = await service.add_reservation_for_a_week("U123")

        assert result.message == "No reservation days available for this week"
        repo.bulk_create.assert_not_awaited()

    async def test_today_after_cutoff_claim_fails_marks_today_pending(
        self, service, repo, settings, wednesday_after_cutoff
    ):
        repo.get_reservations_by_dates.return_value = []
        repo.claim_cancelled_reservation.return_value = False
        week_dates = [
            date(2026, 7, 22),
            date(2026, 7, 23),
            date(2026, 7, 24),
        ]

        with _patch_clock_and_cache(
            settings,
            [],
            wednesday_after_cutoff,
            week_dates=week_dates,
        ):
            result = await service.add_reservation_for_a_week("U123")

        assert "Successfully added the food count" in result.message
        created = repo.bulk_create.await_args.args[0]
        by_date = {r.reservation_date: r.status for r in created}
        assert by_date[date(2026, 7, 22)] == ReservationStatus.PENDING
        assert by_date[date(2026, 7, 23)] == ReservationStatus.CONFIRMED
        assert by_date[date(2026, 7, 24)] == ReservationStatus.CONFIRMED


class TestCancelReservation:
    async def test_no_reservation_returns_message(
        self, service, repo, settings, wednesday_before_cutoff
    ):
        repo.get_reservation_by_date.return_value = None
        with _patch_clock_and_cache(settings, [], wednesday_before_cutoff):
            result = await service.cancel_reservation("U123")

        assert result.message == "You have not given the food count yet"
        repo.delete.assert_not_awaited()

    async def test_outside_waiting_list_window_deletes(
        self, service, repo, settings, wednesday_before_cutoff
    ):
        reservation = make_reservation(reservation_date=date(2026, 7, 22))
        repo.get_reservation_by_date.return_value = reservation
        with _patch_clock_and_cache(settings, [], wednesday_before_cutoff):
            result = await service.cancel_reservation("U123")

        assert result.message == "Successfully cancelled the food count"
        repo.delete.assert_awaited_once_with(reservation)
        repo.update.assert_not_awaited()

    async def test_same_day_window_pending_deletes(
        self, service, repo, settings, wednesday_in_waiting_list_window
    ):
        reservation = make_reservation(
            reservation_date=date(2026, 7, 22),
            status=ReservationStatus.PENDING,
        )
        repo.get_reservation_by_date.return_value = reservation

        with _patch_clock_and_cache(
            settings,
            [],
            wednesday_in_waiting_list_window,
            next_reservation_date=date(2026, 7, 22),
        ):
            result = await service.cancel_reservation("U123")

        assert result.message == "Successfully cancelled the food count"
        repo.delete.assert_awaited_once_with(reservation)

    async def test_same_day_window_confirmed_promote_true_deletes(
        self,
        service,
        repo,
        background_tasks,
        settings,
        wednesday_in_waiting_list_window,
    ):
        reservation = make_reservation(
            reservation_date=date(2026, 7, 22),
            status=ReservationStatus.CONFIRMED,
        )
        repo.get_reservation_by_date.return_value = reservation
        pending = make_reservation(
            reservation_id=2,
            slack_user_id="U999",
            reservation_date=date(2026, 7, 22),
            status=ReservationStatus.PENDING,
        )
        repo.get_pending_reservation_for_promotion.return_value = pending

        with _patch_clock_and_cache(
            settings,
            [],
            wednesday_in_waiting_list_window,
            next_reservation_date=date(2026, 7, 22),
        ):
            result = await service.cancel_reservation("U123")

        assert result.message == "Successfully cancelled the food count"
        assert pending.status == ReservationStatus.CONFIRMED
        repo.update.assert_awaited_once_with(pending)
        repo.delete.assert_awaited_once_with(reservation)
        background_tasks.add_task.assert_called_once_with(
            notify,
            "Your reservation is confirmed for today's lunch",
            "U999",
        )

    async def test_same_day_window_confirmed_promote_false_cancels(
        self, service, repo, settings, wednesday_in_waiting_list_window
    ):
        reservation = make_reservation(
            reservation_date=date(2026, 7, 22),
            status=ReservationStatus.CONFIRMED,
        )
        repo.get_reservation_by_date.return_value = reservation
        repo.get_pending_reservation_for_promotion.return_value = None

        with _patch_clock_and_cache(
            settings,
            [],
            wednesday_in_waiting_list_window,
            next_reservation_date=date(2026, 7, 22),
        ):
            result = await service.cancel_reservation("U123")

        assert result.message == "Successfully cancelled the food count"
        assert reservation.status == ReservationStatus.CANCELLED
        repo.update.assert_awaited_once_with(reservation)
        repo.delete.assert_not_awaited()


class TestCancelReservationsForWeek:
    async def test_no_reservations_returns_message(
        self, service, repo, settings, wednesday_before_cutoff
    ):
        repo.get_reservations_by_dates.return_value = []
        with _patch_clock_and_cache(settings, [], wednesday_before_cutoff):
            result = await service.cancel_reservations_for_week("U123")

        assert result.message == ("You have not given the food count for this week")
        repo.bulk_delete.assert_not_awaited()

    async def test_after_cutoff_promote_fails_cancels_today_and_deletes_all(
        self, service, repo, settings, wednesday_after_cutoff
    ):
        today_res = make_reservation(
            reservation_id=1,
            reservation_date=date(2026, 7, 22),
            status=ReservationStatus.CONFIRMED,
        )
        tomorrow_res = make_reservation(
            reservation_id=2,
            reservation_date=date(2026, 7, 23),
            status=ReservationStatus.CONFIRMED,
        )
        repo.get_reservations_by_dates.return_value = [today_res, tomorrow_res]
        repo.get_reservation_by_date.return_value = today_res
        repo.get_pending_reservation_for_promotion.return_value = None

        with _patch_clock_and_cache(
            settings,
            [],
            wednesday_after_cutoff,
            week_dates=[date(2026, 7, 22), date(2026, 7, 23), date(2026, 7, 24)],
        ):
            result = await service.cancel_reservations_for_week("U123")

        assert result.message == ("Successfully cancelled the food count for this week")
        assert today_res.status == ReservationStatus.CANCELLED
        repo.update.assert_awaited_once_with(today_res)
        # promote failed → keep_id is None → all reservation ids are bulk-deleted
        assert set(repo.bulk_delete.await_args.args[0]) == {1, 2}


class TestPromotePendingReservations:
    async def test_no_pending_returns_false(self, service, repo, background_tasks):
        repo.get_pending_reservation_for_promotion.return_value = None
        assert (await service.promote_pending_reservations(date(2026, 7, 22))) is False
        repo.update.assert_not_awaited()
        background_tasks.add_task.assert_not_called()

    async def test_pending_promoted_to_confirmed(self, service, repo, background_tasks):
        pending = make_reservation(
            slack_user_id="U999",
            reservation_date=date(2026, 7, 22),
            status=ReservationStatus.PENDING,
        )
        repo.get_pending_reservation_for_promotion.return_value = pending

        assert (await service.promote_pending_reservations(date(2026, 7, 22))) is True
        assert pending.status == ReservationStatus.CONFIRMED
        repo.update.assert_awaited_once_with(pending)
        background_tasks.add_task.assert_called_once_with(
            notify,
            "Your reservation is confirmed for today's lunch",
            "U999",
        )
