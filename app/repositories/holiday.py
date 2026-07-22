from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.holiday import Holiday


class HolidayRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Holiday]:
        stmt = select(Holiday)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, holiday_id: int) -> Holiday | None:
        stmt = select(Holiday).where(Holiday.id == holiday_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, holiday: Holiday) -> Holiday:
        self.session.add(holiday)
        await self.session.flush()
        await self.session.refresh(holiday)
        return holiday

    async def delete(self, holiday: Holiday) -> None:
        await self.session.delete(holiday)
        await self.session.flush()
