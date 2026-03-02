from typing import List, Optional

from sqlalchemy.orm import Session

from app.application.interfaces.user_repository import IUserRepository
from app.domain.models.user import User
from app.domain.models.api_key import APIKey


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_login(self, login: str) -> Optional[User]:
        login_lower = login.lower()
        return self.db.query(User).filter(
            (User.email == login) | (User.username == login_lower)
        ).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_api_key_by_id(self, key_id: int) -> Optional[APIKey]:
        return self.db.query(APIKey).filter(APIKey.id == key_id).first()

    def get_api_keys_by_user_id(self, user_id: int) -> List[APIKey]:
        return self.db.query(APIKey).filter(APIKey.user_id == user_id).all()

    def create_api_key(self, api_key: APIKey) -> APIKey:
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        return api_key

    def save_api_key(self, api_key: APIKey) -> None:
        self.db.commit()
