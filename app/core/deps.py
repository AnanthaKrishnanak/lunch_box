from typing import Annotated

from fastapi import Depends
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.slack import get_slack_client
from app.repositories.user import UserRepository
from app.services.user import UserService

Session = Annotated[AsyncSession, Depends(get_session)]


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

SlackClientDeps = Annotated[
    AsyncWebClient,
    Depends(get_slack_client),
]
