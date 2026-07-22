from fastapi import HTTPException
from starlette import status

from app.models.holiday import Holiday
from app.repositories.holiday import HolidayRepository
from app.schemas.holiday import HolidayBase


class HolidayService:
    def __init__(self, holiday_repository: HolidayRepository):
        self.repository = holiday_repository

    async def get_all(self) -> list[Holiday]:
        return await self.repository.get_all()

    async def get_by_id(self, holiday_id: int) -> Holiday:
        holiday = await self.repository.get_by_id(holiday_id)
        if holiday is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Holiday with id {holiday_id} not found",
            )
        return holiday

    async def create(self, payload: HolidayBase) -> Holiday:
        from app.core.cache import (
            invalidate_holidays_cache,
        )  # deferred to avoid circular import

        holiday = Holiday(**payload.model_dump())
        await self.repository.create(holiday)
        invalidate_holidays_cache()
        return holiday

    async def delete(self, holiday_id: int) -> None:
        from app.core.cache import (
            invalidate_holidays_cache,
        )  # deferred to avoid circular import

        holiday = await self.get_by_id(holiday_id)
        await self.repository.delete(holiday)
        invalidate_holidays_cache()
