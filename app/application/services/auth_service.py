from datetime import datetime, timedelta, timezone
from typing import Optional
from secrets import token_urlsafe

from fastapi import HTTPException, status

from app.domain.models.user import User, UserRole
from app.domain.models.api_key import APIKey
from app.application.interfaces.user_repository import IUserRepository
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.api.auth_schema import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserWithTokenResponse,
    UserResponse,
    APIKeyCreate,
    APIKeyCreatedResponse
)


class AuthService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    # =========================================================================
    # User Registration & Login
    # =========================================================================

    async def register_user(self, user_data: UserRegister) -> UserWithTokenResponse:
        if await self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        if await self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=UserRole.FORM_CREATOR,
            is_active=True,
            is_verified=False
        )
        new_user = await self.user_repo.create(new_user)

        access_token = create_access_token(data={"sub": str(new_user.id)})
        refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

        return UserWithTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(new_user)
        )

    async def login_user(self, login_data: UserLogin) -> UserWithTokenResponse:
        user = await self.user_repo.get_by_login(login_data.login)

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated"
            )

        user.last_login = datetime.utcnow()
        await self.user_repo.save(user)

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return UserWithTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )

            user_id = payload.get("sub")
            user = await self.user_repo.get_by_id(int(user_id))

            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

            new_access_token = create_access_token(data={"sub": str(user.id)})
            new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            )

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

    # =========================================================================
    # User Profile Management
    # =========================================================================

    async def change_password(self, user: User, old_password: str, new_password: str) -> bool:
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )

        user.hashed_password = get_password_hash(new_password)
        await self.user_repo.save(user)
        return True

    async def update_profile(
        self,
        user: User,
        full_name: Optional[str] = None,
        username: Optional[str] = None
    ) -> User:
        if full_name is not None:
            user.full_name = full_name

        if username is not None:
            existing = await self.user_repo.get_by_username(username)
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = username

        return await self.user_repo.save(user)

    # =========================================================================
    # API Key Management
    # =========================================================================

    async def create_api_key(self, user: User, key_data: APIKeyCreate) -> APIKeyCreatedResponse:
        key = f"ff_{token_urlsafe(32)}"

        expires_at = None
        if key_data.expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=key_data.expires_in_days)

        api_key = APIKey(
            key=key,
            name=key_data.name,
            user_id=user.id,
            scopes=key_data.scopes,
            expires_at=expires_at
        )
        api_key = await self.user_repo.create_api_key(api_key)

        return APIKeyCreatedResponse(
            id=api_key.id,
            key=key,
            name=api_key.name,
            scopes=api_key.scopes,
            expires_at=api_key.expires_at
        )

    async def list_api_keys(self, user: User) -> list[APIKey]:
        return await self.user_repo.get_api_keys_by_user_id(user.id)

    async def revoke_api_key(self, user: User, key_id: int) -> bool:
        api_key = await self.user_repo.get_api_key_by_id(key_id)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        if api_key.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        api_key.is_active = False
        await self.user_repo.save_api_key(api_key)
        return True
