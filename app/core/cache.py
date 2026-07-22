from async_lru import alru_cache

from app.core.db import SessionLocal
from app.core.settings import settings
from app.models.holiday import Holiday
from app.models.system_settings import SystemSettings
from app.repositories.holiday import HolidayRepository
from app.repositories.system_settings import SystemSettingsRepository
from app.services.holiday import HolidayService
from app.services.system_settings import SystemSettingsService

# Read-through cache only. Mutating settings/holidays must call the matching
# invalidate_* helper so reservation flows never use stale cutoff/holiday data
# as if it were authoritative after a write.
cache = alru_cache(maxsize=settings.LRU_CACHE_SIZE, ttl=settings.LRU_CACHE_TTL)


@cache
async def get_system_settings() -> SystemSettings:
    async with SessionLocal() as session:
        repository = SystemSettingsRepository(session)
        service = SystemSettingsService(repository)
        system_settings = await service.get()
        if system_settings is None:
            raise ValueError("System settings not found")
        return system_settings


@cache
async def get_holidays() -> list[Holiday]:
    async with SessionLocal() as session:
        repository = HolidayRepository(session)
        service = HolidayService(repository)
        return await service.get_all()


def invalidate_system_settings_cache() -> None:
    get_system_settings.cache_clear()


def invalidate_holidays_cache() -> None:
    get_holidays.cache_clear()
