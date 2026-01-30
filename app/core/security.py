"""
Security modul za autentifikaciju i autorizaciju.

Sadrži:
- Password hashing (bcrypt)
- JWT token kreiranje i verifikacija
- Dependencies za FastAPI route protection
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infrastructure.database.session import get_db
from app.domain.models.user import User, UserRole


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer security scheme
security = HTTPBearer()


# =============================================================================
# Password Functions
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikuje da li plain password odgovara hash-u."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashuje password koristeći bcrypt."""
    return pwd_context.hash(password)


# =============================================================================
# JWT Token Functions
# =============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Kreira JWT access token.
    
    Args:
        data: Podaci koji se enkoduju u token (obično {"sub": user_id})
        expires_delta: Opciono, custom vreme isteka
    
    Returns:
        Enkodovani JWT token string
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
    Kreira JWT refresh token sa dužim vremenom isteka.
    
    Args:
        data: Podaci koji se enkoduju u token
    
    Returns:
        Enkodovani JWT refresh token string
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
    Dekoduje i validira JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dekodirani payload
    
    Raises:
        JWTError: Ako je token nevažeći ili istekao
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
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency za dobijanje trenutno ulogovanog korisnika.
    
    Koristi se kao: current_user: User = Depends(get_current_user)
    
    Raises:
        HTTPException 401: Ako token nije validan
        HTTPException 401: Ako korisnik ne postoji
        HTTPException 400: Ako je korisnik neaktivan
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        
        # Proveri da li je access token
        if payload.get("type") != "access":
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Dohvati korisnika iz baze
    user = db.query(User).filter(User.id == int(user_id)).first()
    
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
    Dependency koji dodatno proverava da li je korisnik aktivan.
    Koristan kao wrapper za get_current_user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: list[UserRole]):
    """
    Factory function za kreiranje dependency-ja koji zahteva određenu rolu.
    
    Koristi se kao: current_user: User = Depends(require_role([UserRole.ADMIN]))
    
    Args:
        allowed_roles: Lista dozvoljenih rola
    
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
# Optional Auth Dependency
# =============================================================================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Opcioni dependency - vraća korisnika ako je ulogovan, None ako nije.
    
    Koristan za endpointe koji rade i sa i bez autentifikacije.
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
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if user and user.is_active:
            return user
        
        return None
        
    except JWTError:
        return None

