from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_slack_user_id(self, slack_user_id: str) -> User | None:
        return await self.user_repository.get_by_slack_user_id(slack_user_id)

    async def create(self, user: UserCreate) -> User:
        existing_user = await self.get_by_slack_user_id(user.slack_user_id)
        if existing_user:
            return existing_user
        return await self.user_repository.create(User(**user.model_dump()))
