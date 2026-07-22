from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import Reservation, ReservationStatus


class ReservationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_reservation_by_date(
        self,
        reservation_date: date,
        slack_user_id: str,
        *,
        for_update: bool = False,
    ) -> Reservation | None:
        stmt = select(Reservation).where(
            Reservation.reservation_date == reservation_date,
            Reservation.slack_user_id == slack_user_id,
        )
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_reservations(self, reservation_date: date) -> list[Reservation]:
        stmt = select(Reservation).where(
            Reservation.reservation_date == reservation_date,
            Reservation.status != ReservationStatus.CANCELLED,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_reservation_for_promotion(
        self,
        reservation_date: date,
    ) -> Reservation | None:
        stmt = (
            select(Reservation)
            .where(
                Reservation.reservation_date == reservation_date,
                Reservation.status == ReservationStatus.PENDING,
            )
            .order_by(Reservation.created_at, Reservation.id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def claim_cancelled_reservation(self, reservation_date: date) -> bool:
        """
        Claim a cancelled reservation when a new pending reservation is created.
        Returns True if a cancelled reservation is claimed, False otherwise.
        """
        stmt = (
            select(Reservation)
            .where(
                Reservation.reservation_date == reservation_date,
                Reservation.status == ReservationStatus.CANCELLED,
            )
            .order_by(
                Reservation.created_at,
                Reservation.id,
            )
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        cancelled_reservation = result.scalars().first()
        if cancelled_reservation is None:
            return False
        await self.delete(cancelled_reservation)
        return True

    async def get_reservations_by_dates(
        self, reservation_dates: list[date], slack_user_id: str
    ) -> list[Reservation]:
        stmt = select(Reservation).where(
            Reservation.reservation_date.in_(reservation_dates),
            Reservation.slack_user_id == slack_user_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, reservation: Reservation) -> Reservation:
        self.session.add(reservation)
        await self.session.flush()
        await self.session.refresh(reservation)
        return reservation

    async def update(self, reservation: Reservation) -> Reservation:
        self.session.add(reservation)
        await self.session.flush()
        await self.session.refresh(reservation)
        return reservation

    async def delete(self, reservation: Reservation) -> None:
        await self.session.delete(reservation)
        await self.session.flush()

    async def bulk_create(self, reservations: list[Reservation]) -> None:
        self.session.add_all(reservations)
        await self.session.flush()

    async def bulk_delete(self, reservation_ids: list[int]) -> None:
        stmt = delete(Reservation).where(Reservation.id.in_(reservation_ids))
        await self.session.execute(stmt)
        await self.session.flush()
