from typing import cast

from fastapi import APIRouter, Request

from app.core.settings import settings
from app.models.user import User
from app.schemas.user import UserRead

user_router = APIRouter(
    prefix=f"{settings.API_VERSION}/user",
    tags=["User"],
)


@user_router.post("", response_model=UserRead)
async def get_current_user(request: Request) -> User:
    return cast(User, request.state.user)
