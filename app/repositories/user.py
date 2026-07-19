from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_slack_user_id(self, slack_user_id: str) -> User | None:
        stmt = select(User).where(User.slack_user_id == slack_user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
