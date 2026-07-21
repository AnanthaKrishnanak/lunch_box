from datetime import date

from app.core.exceptions import NotFoundError
from app.core.time import now, today
from app.models.reservation import Reservation, ReservationStatus
from app.repositories.reservation import ReservationRepository
from app.schemas.reservation import ReservationResponse
from app.utils.reservation import (
    get_next_reservation_date,
    get_next_reservation_dates_for_a_week,
)


class ReservationService:
    def __init__(self, reservation_repository: ReservationRepository):
        self.reservation_repository = reservation_repository

    async def get_reservation_by_date(
        self, reservation_date: date, slack_user_id: str
    ) -> Reservation | None:
        return await self.reservation_repository.get_reservation_by_date(
            reservation_date, slack_user_id
        )

    async def get_all_reservations(self) -> list[Reservation]:
        return await self.reservation_repository.get_all_reservations(today())

    async def add_reservation(self, slack_user_id: str) -> ReservationResponse:
        from app.core.cache import (
            get_holidays,
            get_system_settings,
        )  # deferred to avoid circular import

        holidays = await get_holidays()
        system_settings = await get_system_settings()

        if system_settings is None:
            raise NotFoundError("System settings not found")

        reservation_date = get_next_reservation_date(
            system_settings,
            holidays,
        )

        existing_reservation = (
            await self.reservation_repository.get_reservation_by_date(
                reservation_date,
                slack_user_id,
            )
        )

        if existing_reservation:
            if existing_reservation.status == ReservationStatus.PENDING:
                return ReservationResponse(
                    message="You are already in the waiting list"
                )

            return ReservationResponse(
                message="You have already given the food count, chill!"
            )

        status = ReservationStatus.CONFIRMED

        is_after_cutoff = (
            reservation_date == today() and now().time() >= system_settings.cutoff_time
        )

        if is_after_cutoff:
            cancelled_reservation = (
                await self.reservation_repository.get_cancelled_reservation(
                    reservation_date=reservation_date,
                )
            )

            if cancelled_reservation:
                await self.reservation_repository.delete(cancelled_reservation)
            else:
                status = ReservationStatus.PENDING

        reservation = Reservation(
            slack_user_id=slack_user_id,
            reservation_date=reservation_date,
            status=status,
        )

        await self.reservation_repository.create(reservation)

        if status == ReservationStatus.PENDING:
            return ReservationResponse(message="You are added to the waiting list")

        return ReservationResponse(
            message=f"Successfully added the food count for {reservation_date}"
        )

    async def add_reservation_for_a_week(
        self, slack_user_id: str
    ) -> ReservationResponse:
        from app.core.cache import (
            get_holidays,
            get_system_settings,
        )  # deferred to avoid circular import

        system_settings = await get_system_settings()
        if system_settings is None:
            raise NotFoundError("System settings not found")

        holidays = await get_holidays()
        reservation_dates = get_next_reservation_dates_for_a_week(
            system_settings,
            holidays,
        )

        existing_reservations = (
            await self.reservation_repository.get_reservations_by_dates(
                reservation_dates=reservation_dates,
                slack_user_id=slack_user_id,
            )
        )

        reservations_to_add = [
            Reservation(
                slack_user_id=slack_user_id,
                reservation_date=reservation_date,
                status=ReservationStatus.CONFIRMED,
            )
            for reservation_date in reservation_dates
            if reservation_date not in existing_reservations
        ]

        if not reservations_to_add and existing_reservations:
            return ReservationResponse(
                message="You have already given the food count for this week"
            )

        if not reservations_to_add:
            return ReservationResponse(
                message="No reservation days available for this week"
            )

        today_reservation = next(
            (
                reservation
                for reservation in reservations_to_add
                if reservation.reservation_date == today()
            ),
            None,
        )

        if today_reservation and now().time() >= system_settings.cutoff_time:
            cancelled_reservation = (
                await self.reservation_repository.get_cancelled_reservation(
                    reservation_date=reservations_to_add[0].reservation_date,
                )
            )

            if cancelled_reservation:
                await self.reservation_repository.delete(cancelled_reservation)
            else:
                today_reservation.status = ReservationStatus.PENDING

        await self.reservation_repository.bulk_create(reservations_to_add)

        formatted_dates = ", ".join(
            str(reservation_date) for reservation_date in reservation_dates
        )
        return ReservationResponse(
            message=f"Successfully added the food count for {formatted_dates}"
        )

    async def cancel_reservation(self, slack_user_id: str) -> ReservationResponse:
        from app.core.cache import (
            get_holidays,
            get_system_settings,
        )  # deferred to avoid circular import

        system_settings = await get_system_settings()
        holidays = await get_holidays()
        current_time = now().time()

        if system_settings is None:
            raise NotFoundError("System settings not found")

        reservation_date = get_next_reservation_date(
            system_settings,
            holidays,
        )

        reservation = await self.get_reservation_by_date(
            reservation_date, slack_user_id
        )

        if reservation is None:
            return ReservationResponse(message="You have not given the food count yet")

        is_same_day_waiting_list_window = (
            reservation.reservation_date == today()
            and system_settings.cutoff_time
            <= current_time
            < system_settings.day_rollover_time
        )

        if is_same_day_waiting_list_window:
            if reservation.status == ReservationStatus.PENDING:
                await self.reservation_repository.delete(reservation)
            else:
                is_promoted = await self.promote_pending_reservations(
                    reservation_date=reservation_date,
                )
                if is_promoted:
                    await self.reservation_repository.delete(reservation)
                else:
                    reservation.status = ReservationStatus.CANCELLED
                    await self.reservation_repository.update(reservation)

        else:
            await self.reservation_repository.delete(reservation)
        return ReservationResponse(message="Successfully cancelled the food count")

    async def cancel_reservations_for_week(
        self, slack_user_id: str
    ) -> ReservationResponse:
        from app.core.cache import (
            get_holidays,
            get_system_settings,
        )  # deferred to avoid circular import

        system_settings = await get_system_settings()
        if system_settings is None:
            raise NotFoundError("System settings not found")

        holidays = await get_holidays()
        reservation_dates = get_next_reservation_dates_for_a_week(
            system_settings,
            holidays,
        )

        reservations = await self.reservation_repository.get_reservations_by_dates(
            reservation_dates=reservation_dates,
            slack_user_id=slack_user_id,
        )

        if not reservations:
            return ReservationResponse(
                message="You have not given the food count for this week"
            )

        todays_reservation = next(
            (
                reservation
                for reservation in reservations
                if reservation.reservation_date == today()
            ),
            None,
        )

        reservation_to_keep = None
        if todays_reservation and now().time() >= system_settings.cutoff_time:
            is_promoted = await self.promote_pending_reservations(
                reservation_date=todays_reservation.reservation_date,
            )

            if not is_promoted:
                todays_reservation.status = ReservationStatus.CANCELLED
                await self.reservation_repository.update(todays_reservation)
            else:
                reservation_to_keep = todays_reservation

        reservation_ids_to_cancel = [
            reservation.id
            for reservation in reservations
            if reservation != reservation_to_keep
        ]

        await self.reservation_repository.bulk_delete(reservation_ids_to_cancel)
        return ReservationResponse(
            message="Successfully cancelled the food count for this week"
        )

    async def promote_pending_reservations(self, reservation_date: date) -> bool:
        "returns true if a reservation was promoted"
        first_pending_reservation = (
            await self.reservation_repository.get_pending_reservation_for_promotion(
                reservation_date,
            )
        )

        if not first_pending_reservation:
            return False

        first_pending_reservation.status = ReservationStatus.CONFIRMED
        await self.reservation_repository.update(first_pending_reservation)

        return True
