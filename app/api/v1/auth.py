"""
Auth API endpoints za registraciju, login, i upravljanje korisnicima.
"""
from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service
from app.core.security import get_current_user
from app.domain.models.user import User
from app.application.services.auth_service import AuthService
from app.api.auth_schema import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    PasswordChange,
    UserUpdate,
    UserWithTokenResponse,
    TokenResponse,
    UserResponse,
    MessageResponse,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyCreatedResponse
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================================
# Registration & Login
# =============================================================================

@router.post(
    "/register",
    response_model=UserWithTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account and return authentication tokens."
)
async def register(
    user_data: UserRegister,
    service: AuthService = Depends(get_auth_service)
):
    """
    Registracija novog korisnika.

    - **email**: Validna email adresa (mora biti jedinstvena)
    - **username**: 3-50 karaktera, samo slova, brojevi i underscore
    - **password**: Min 8 karaktera, mora sadržati veliko slovo, malo slovo i broj
    - **full_name**: Opciono, puno ime korisnika
    """
    return service.register_user(user_data)


@router.post(
    "/login",
    response_model=UserWithTokenResponse,
    summary="Login user",
    description="Authenticate user with email or username and return access and refresh tokens."
)
async def login(
    login_data: UserLogin,
    service: AuthService = Depends(get_auth_service)
):
    """
    Login korisnika sa email/username i password.

    - **login**: Email adresa ili username
    - **password**: Lozinka korisnika

    Vraća access token (kratko traje) i refresh token (dugo traje).
    """
    return service.login_user(login_data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Use refresh token to get a new access token."
)
async def refresh_token(
    token_data: TokenRefresh,
    service: AuthService = Depends(get_auth_service)
):
    """
    Osvežavanje access tokena koristeći refresh token.

    Koristi se kada access token istekne da se dobije novi
    bez ponovnog unosa lozinke.
    """
    return service.refresh_access_token(token_data.refresh_token)


# =============================================================================
# Current User Profile
# =============================================================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information."
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Dohvata informacije o trenutno ulogovanom korisniku.
    
    Zahteva validan access token u Authorization headeru.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update the currently authenticated user's profile."
)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """
    Ažurira profil trenutnog korisnika.

    Može se promeniti:
    - **full_name**: Puno ime
    - **username**: Korisničko ime (mora biti jedinstveno)
    """
    return service.update_profile(
        user=current_user,
        full_name=update_data.full_name,
        username=update_data.username
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change the current user's password."
)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """
    Promena lozinke trenutnog korisnika.

    - **old_password**: Trenutna lozinka za verifikaciju
    - **new_password**: Nova lozinka (min 8 karaktera, mora sadržati veliko slovo, malo slovo i broj)
    """
    service.change_password(
        user=current_user,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    return MessageResponse(message="Password changed successfully")


# =============================================================================
# API Keys Management
# =============================================================================

@router.post(
    "/api-keys",
    response_model=APIKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key",
    description="Create a new API key for programmatic access."
)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """
    Kreira novi API ključ za programatski pristup.

    ⚠️ **VAŽNO**: Ključ se prikazuje samo jednom! Sačuvajte ga na sigurno mesto.

    - **name**: Opis za šta se koristi ključ
    - **scopes**: Lista dozvola (read, write, delete)
    - **expires_in_days**: Opciono, koliko dana važi ključ (1-365)
    """
    return service.create_api_key(current_user, key_data)


@router.get(
    "/api-keys",
    response_model=list[APIKeyResponse],
    summary="List API keys",
    description="List all API keys for the current user."
)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """
    Lista svih API ključeva trenutnog korisnika.

    Ne prikazuje same ključeve, samo metapodatke.
    """
    return service.list_api_keys(current_user)


@router.delete(
    "/api-keys/{key_id}",
    response_model=MessageResponse,
    summary="Revoke API key",
    description="Deactivate an API key."
)
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """
    Deaktivira API ključ.

    Deaktivirani ključ više ne može da se koristi za autentifikaciju.
    """
    service.revoke_api_key(current_user, key_id)
    return MessageResponse(message="API key revoked successfully")


