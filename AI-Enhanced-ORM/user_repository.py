from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_models import User
from resp_models import UserCreate


class UserRepository:

    def __init__(self, db: AsyncSession):

        self.db = db

    async def create(self, user_create: UserCreate) -> User:
        user = User(
            name=user_create.name,
            email=user_create.email
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()
    async def get_all_users(self,skip: int = 0, limit: int = 10) -> list[User]:
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
