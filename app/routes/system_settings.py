from fastapi import APIRouter
from starlette import status

from app.core.deps import SystemSettingsServiceDeps
from app.core.settings import settings
from app.models.system_settings import SystemSettings
from app.schemas.system_settings import SystemSettingsBase, SystemSettingsRead

system_settings_router = APIRouter(
    prefix=f"{settings.API_VERSION}/system_settings",
    tags=["System Settings"],
)


@system_settings_router.get("/", response_model=SystemSettingsRead)
async def get_system_settings(
    system_settings_service: SystemSettingsServiceDeps,
) -> SystemSettings | None:
    return await system_settings_service.get()


@system_settings_router.post(
    "/", response_model=SystemSettingsRead, status_code=status.HTTP_201_CREATED
)
async def create_system_settings(
    system_settings_service: SystemSettingsServiceDeps,
    payload: SystemSettingsBase,
) -> SystemSettings:
    return await system_settings_service.create(payload)


@system_settings_router.put(
    "/", response_model=SystemSettingsRead, status_code=status.HTTP_200_OK
)
async def update_system_settings(
    system_settings_service: SystemSettingsServiceDeps,
    payload: SystemSettingsBase,
) -> SystemSettings:
    return await system_settings_service.update(payload)


@system_settings_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_settings(
    system_settings_service: SystemSettingsServiceDeps,
) -> None:
    return await system_settings_service.delete()
