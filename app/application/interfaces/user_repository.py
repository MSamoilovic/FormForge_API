from abc import ABC, abstractmethod

from app.domain.models.api_key import APIKey
from app.domain.models.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_login(self, login: str) -> User | None:
        """Traži korisnika po email-u ILI username-u (za login)."""

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Commit-uje izmene na postojećem korisniku."""

    @abstractmethod
    async def get_api_key_by_id(self, key_id: int) -> APIKey | None:
        pass

    @abstractmethod
    async def get_api_keys_by_user_id(self, user_id: int) -> list[APIKey]:
        pass

    @abstractmethod
    async def create_api_key(self, api_key: APIKey) -> APIKey:
        pass

    @abstractmethod
    async def save_api_key(self, api_key: APIKey) -> None:
        pass
