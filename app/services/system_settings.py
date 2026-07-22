from app.models.system_settings import SystemSettings
from app.repositories.system_settings import SystemSettingsRepository
from app.schemas.system_settings import SystemSettingsBase


class SystemSettingsService:
    def __init__(self, system_settings_repository: SystemSettingsRepository):
        self.repository = system_settings_repository

    async def get(self) -> SystemSettings | None:
        return await self.repository.get()

    async def create(self, payload: SystemSettingsBase) -> SystemSettings:
        from app.core.cache import (
            invalidate_system_settings_cache,
        )  # deferred to avoid circular import

        system_settings = SystemSettings(**payload.model_dump())
        created_system_settings = await self.repository.create(system_settings)
        invalidate_system_settings_cache()
        return created_system_settings

    async def update(self, payload: SystemSettingsBase) -> SystemSettings:
        from app.core.cache import (
            invalidate_system_settings_cache,
        )  # deferred to avoid circular import

        system_settings = await self.repository.get()

        if system_settings is None:
            system_settings = await self.create(payload)

        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(system_settings, field, value)

        updated_system_settings = await self.repository.update(system_settings)
        invalidate_system_settings_cache()
        return updated_system_settings

    async def delete(self) -> None:
        from app.core.cache import (
            invalidate_system_settings_cache,
        )  # deferred to avoid circular import

        system_settings = await self.repository.get()
        if system_settings is None:
            return None
        await self.repository.delete(system_settings)
        invalidate_system_settings_cache()
