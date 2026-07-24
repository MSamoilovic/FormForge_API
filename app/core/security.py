"""
Security module for authentication and authorization.

Contains:
- Password hashing (bcrypt)
- JWT token creation and verification
- Dependencies for FastAPI route protection
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.infrastructure.database.session import get_db
from app.domain.models.user import User, UserRole
from app.domain.models.api_key import APIKey


# HTTP Bearer security scheme
security = HTTPBearer()

# API key security scheme (M2M authentication via the X-API-Key header)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that a plain password matches the hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')


# =============================================================================
# JWT Token Functions
# =============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data: Payload encoded into the token (usually {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Creates a JWT refresh token with a longer expiration time.

    Args:
        data: Payload encoded into the token

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload

    Raises:
        JWTError: If the token is invalid or expired
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )


# =============================================================================
# FastAPI Dependencies
# =============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency that returns the currently logged-in user.

    Used as: current_user: User = Depends(get_current_user)

    Raises:
        HTTPException 401: If the token is invalid
        HTTPException 401: If the user does not exist
        HTTPException 400: If the user is inactive
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = decode_token(token)

        # Make sure this is an access token
        if payload.get("type") != "access":
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that additionally checks whether the user is active.
    Useful as a wrapper around get_current_user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: list[UserRole]):
    """
    Factory function that builds a dependency requiring a specific role.

    Used as: current_user: User = Depends(require_role([UserRole.ADMIN]))

    Args:
        allowed_roles: List of allowed roles

    Returns:
        FastAPI dependency function
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user

    return role_checker


# =============================================================================
# API Key / M2M Authentication
# =============================================================================

@dataclass
class AuthContext:
    """Result of authenticating a request.

    `via_api_key` distinguishes an M2M call (authenticated with an API key)
    from a human session (JWT). `scopes` is only meaningful for API keys —
    JWT users act with the full authority of their account.
    """
    user: User
    via_api_key: bool = False
    scopes: list[str] = field(default_factory=list)


async def _authenticate_api_key(api_key: str, db: AsyncSession) -> Optional[tuple[User, APIKey]]:
    """Resolve an API key string to its (user, key) pair, or None if invalid."""
    result = await db.execute(select(APIKey).filter(APIKey.key == api_key))
    key_obj = result.scalar_one_or_none()

    # is_valid covers both is_active and expiry (see APIKey model)
    if key_obj is None or not key_obj.is_valid:
        return None

    result = await db.execute(select(User).filter(User.id == key_obj.user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        return None

    return user, key_obj


async def get_auth_context(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    api_key: Optional[str] = Depends(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    """
    Authenticate a request via either a JWT Bearer token or an API key.

    A Bearer token takes precedence when both are present. Raises 401 if
    neither credential resolves to an active user.
    """
    # --- JWT Bearer ---
    if bearer is not None:
        try:
            payload = decode_token(bearer.credentials)
            if payload.get("type") == "access":
                user_id = payload.get("sub")
                if user_id is not None:
                    result = await db.execute(select(User).filter(User.id == int(user_id)))
                    user = result.scalar_one_or_none()
                    if user and user.is_active:
                        return AuthContext(user=user)
        except JWTError:
            pass

    # --- API key ---
    if api_key:
        auth = await _authenticate_api_key(api_key, db)
        if auth is not None:
            user, key_obj = auth
            key_obj.last_used_at = datetime.utcnow()
            await db.commit()
            return AuthContext(
                user=user,
                via_api_key=True,
                scopes=list(key_obj.scopes or []),
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_scope(scope: str):
    """
    Factory that builds a dependency requiring a given scope.

    JWT-authenticated users always pass (scopes are an API-key concept).
    API-key requests must carry the scope in their granted list.

    Used as: current_user: User = Depends(require_scope("write"))
    """
    async def scope_checker(ctx: AuthContext = Depends(get_auth_context)) -> User:
        if ctx.via_api_key and scope not in ctx.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key is missing the required scope: '{scope}'",
            )
        return ctx.user

    return scope_checker


# =============================================================================
# Optional Auth Dependency
# =============================================================================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional dependency - returns the user if logged in, None otherwise.

    Useful for endpoints that work both with and without authentication.
    """
    if credentials is None:
        return None

    try:
        payload = decode_token(credentials.credentials)

        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        result = await db.execute(select(User).filter(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if user and user.is_active:
            return user

        return None

    except JWTError:
        return None

