from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_settings import SystemSettings


class SystemSettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self) -> SystemSettings | None:
        stmt = select(SystemSettings).order_by(SystemSettings.updated_at)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, system_settings: SystemSettings) -> SystemSettings:
        self.session.add(system_settings)
        await self.session.flush()
        await self.session.refresh(system_settings)
        return system_settings

    async def update(self, system_settings: SystemSettings) -> SystemSettings:
        self.session.add(system_settings)
        await self.session.flush()
        await self.session.refresh(system_settings)
        return system_settings

    async def delete(self, system_settings: SystemSettings) -> None:
        await self.session.delete(system_settings)
        await self.session.flush()
