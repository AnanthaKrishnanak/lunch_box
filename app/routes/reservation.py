from fastapi import APIRouter, Request

from app.core.deps import ReservationServiceDeps
from app.core.settings import settings
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationResponse

reservation_router = APIRouter(
    prefix=f"{settings.API_VERSION}/reservation",
    tags=["Reservation"],
)


@reservation_router.post("/add_count", response_model=ReservationResponse)
async def add_count(
    service: ReservationServiceDeps, request: Request
) -> ReservationResponse:
    return await service.add_reservation(request.state.user.slack_user_id)


@reservation_router.post("/cancel_count", response_model=ReservationResponse)
async def cancel_count(
    service: ReservationServiceDeps, request: Request
) -> ReservationResponse:
    return await service.cancel_reservation(request.state.user.slack_user_id)


@reservation_router.post("/add_count_for_a_week", response_model=ReservationResponse)
async def add_count_for_a_week(
    service: ReservationServiceDeps, request: Request
) -> ReservationResponse:
    return await service.add_reservation_for_a_week(request.state.user.slack_user_id)


@reservation_router.post("/cancel_count_for_a_week", response_model=ReservationResponse)
async def cancel_count_for_a_week(
    service: ReservationServiceDeps, request: Request
) -> ReservationResponse:
    return await service.cancel_reservations_for_week(request.state.user.slack_user_id)


@reservation_router.post("/get_all_reservations", response_model=None)  # todo fix type
async def get_all_reservations(service: ReservationServiceDeps) -> list[Reservation]:
    return await service.get_all_reservations()
