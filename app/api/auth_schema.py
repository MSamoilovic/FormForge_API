"""
Pydantic schemas za autentifikaciju i korisničke operacije.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from app.domain.models.user import UserRole


# =============================================================================
# Request Schemas
# =============================================================================

class UserRegister(BaseModel):
    """Schema za registraciju novog korisnika."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Username može sadržati samo slova, brojeve i underscore."""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v.lower()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Password mora imati bar jedno veliko slovo, malo slovo i broj."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema za login (email ili username + password)."""
    login: str = Field(..., description="Email ili username")
    password: str


class TokenRefresh(BaseModel):
    """Schema za refresh token request."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Schema za promenu passworda."""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Iste validacije kao za registraciju."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema za ažuriranje korisničkog profila."""
    full_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r"^[a-zA-Z0-9_]+$", v):
                raise ValueError("Username can only contain letters, numbers, and underscores")
            return v.lower()
        return v


# =============================================================================
# Response Schemas
# =============================================================================

class TokenResponse(BaseModel):
    """Response sa access i refresh tokenima."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    """Response samo sa access tokenom (za refresh)."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response schema za korisničke podatke."""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    organization_id: Optional[int] = None
    
    model_config = {"from_attributes": True}


class UserWithTokenResponse(BaseModel):
    """Response za registraciju/login sa tokenima i user info."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Generički response sa porukom."""
    message: str


# =============================================================================
# API Key Schemas
# =============================================================================

class APIKeyCreate(BaseModel):
    """Schema za kreiranje API ključa."""
    name: str = Field(..., min_length=1, max_length=100)
    scopes: list[str] = Field(default=["read"])
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """Response za API ključ (bez samog ključa)."""
    id: int
    name: str
    scopes: list[str]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class APIKeyCreatedResponse(BaseModel):
    """Response kada se kreira novi API ključ (uključuje sam ključ)."""
    id: int
    key: str  # Prikazuje se samo jednom!
    name: str
    scopes: list[str]
    expires_at: Optional[datetime] = None
    message: str = "Store this key securely. It won't be shown again."


