from fastapi import APIRouter
from starlette import status

from app.core.deps import HolidayServiceDeps
from app.core.settings import settings
from app.models.holiday import Holiday
from app.schemas.holiday import HolidayBase

holiday_router = APIRouter(
    prefix=f"{settings.API_VERSION}/holiday",
    tags=["Holiday"],
)


@holiday_router.get(
    "/",
    response_model=list[HolidayBase],
)
async def get_all_holidays(
    holiday_service: HolidayServiceDeps,
) -> list[Holiday]:
    return await holiday_service.get_all()


@holiday_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=HolidayBase
)
async def create_holiday(
    holiday_service: HolidayServiceDeps,
    holiday: HolidayBase,
) -> Holiday:
    return await holiday_service.create(holiday)


@holiday_router.delete("/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
    holiday_service: HolidayServiceDeps,
    holiday_id: int,
) -> None:
    return await holiday_service.delete(holiday_id)
