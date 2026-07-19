from typing import Annotated

from fastapi import Depends
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.slack import get_slack_client
from app.repositories.holiday import HolidayRepository
from app.repositories.system_settings import SystemSettingsRepository
from app.repositories.user import UserRepository
from app.services.holiday import HolidayService
from app.services.system_settings import SystemSettingsService
from app.services.user import UserService

# DB session

Session = Annotated[AsyncSession, Depends(get_session)]


# User
def get_user_repository(session: Session) -> UserRepository:
    return UserRepository(session)


UserRepositoryDeps = Annotated[
    UserRepository,
    Depends(get_user_repository),
]


def get_user_service(
    user_repository: UserRepositoryDeps,
) -> UserService:
    return UserService(user_repository)


UserServiceDeps = Annotated[
    UserService,
    Depends(get_user_service),
]

# Slack Client

SlackClientDeps = Annotated[
    AsyncWebClient,
    Depends(get_slack_client),
]


# System Settings
def get_system_settings_repository(session: Session) -> SystemSettingsRepository:
    return SystemSettingsRepository(session)


SystemSettingsRepositoryDeps = Annotated[
    SystemSettingsRepository,
    Depends(get_system_settings_repository),
]


def get_system_settings_service(
    system_settings_repository: SystemSettingsRepositoryDeps,
) -> SystemSettingsService:
    return SystemSettingsService(system_settings_repository)


SystemSettingsServiceDeps = Annotated[
    SystemSettingsService,
    Depends(get_system_settings_service),
]

# Holiday


def get_holiday_repository(session: Session) -> HolidayRepository:
    return HolidayRepository(session)


HolidayRepositoryDeps = Annotated[
    HolidayRepository,
    Depends(get_holiday_repository),
]


def get_holiday_service(
    holiday_repository: HolidayRepositoryDeps,
) -> HolidayService:
    return HolidayService(holiday_repository)


HolidayServiceDeps = Annotated[
    HolidayService,
    Depends(get_holiday_service),
]
