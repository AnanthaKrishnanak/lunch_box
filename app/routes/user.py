from fastapi import APIRouter

from app.core.deps import UserServiceDeps
from app.core.settings import settings
from app.models.user import User
from app.schemas.user import UserCreate

user_router = APIRouter(
    prefix=f"{settings.API_VERSION}/user",
    tags=["User"],
)


@user_router.get("/{slack_user_id}")
async def get_user(slack_user_id: str, user_service: UserServiceDeps) -> User | None:
    return await user_service.get_by_slack_user_id(slack_user_id)


@user_router.post("/")
async def create_user(user: UserCreate, user_service: UserServiceDeps) -> User:
    return await user_service.create(user)
