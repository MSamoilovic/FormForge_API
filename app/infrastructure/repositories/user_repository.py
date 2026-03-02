from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.application.interfaces.user_repository import IUserRepository
from app.domain.models.user import User
from app.domain.models.api_key import APIKey


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_login(self, login: str) -> Optional[User]:
        login_lower = login.lower()
        result = await self.db.execute(
            select(User).filter((User.email == login) | (User.username == login_lower))
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def save(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_api_key_by_id(self, key_id: int) -> Optional[APIKey]:
        result = await self.db.execute(select(APIKey).filter(APIKey.id == key_id))
        return result.scalar_one_or_none()

    async def get_api_keys_by_user_id(self, user_id: int) -> List[APIKey]:
        result = await self.db.execute(select(APIKey).filter(APIKey.user_id == user_id))
        return result.scalars().all()

    async def create_api_key(self, api_key: APIKey) -> APIKey:
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key

    async def save_api_key(self, api_key: APIKey) -> None:
        await self.db.commit()
