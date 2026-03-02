from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models.user import User
from app.domain.models.api_key import APIKey


class IUserRepository(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_login(self, login: str) -> Optional[User]:
        """Traži korisnika po email-u ILI username-u (za login)."""
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Commit-uje izmene na postojećem korisniku."""
        pass

    @abstractmethod
    async def get_api_key_by_id(self, key_id: int) -> Optional[APIKey]:
        pass

    @abstractmethod
    async def get_api_keys_by_user_id(self, user_id: int) -> List[APIKey]:
        pass

    @abstractmethod
    async def create_api_key(self, api_key: APIKey) -> APIKey:
        pass

    @abstractmethod
    async def save_api_key(self, api_key: APIKey) -> None:
        pass
