"""
Service layer za autentifikaciju i korisničke operacije.
"""
from datetime import datetime, timedelta
from typing import Optional
from secrets import token_urlsafe

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domain.models.user import User, UserRole
from app.domain.models.api_key import APIKey
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
    """Service za autentifikaciju i upravljanje korisnicima."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # User Registration & Login
    # =========================================================================
    
    def register_user(self, user_data: UserRegister) -> UserWithTokenResponse:
        """
        Registruje novog korisnika.
        
        Args:
            user_data: Podaci za registraciju
        
        Returns:
            UserWithTokenResponse sa tokenima i user info
        
        Raises:
            HTTPException 400: Ako email ili username već postoje
        """
        # Proveri da li email već postoji
        existing_email = self.db.query(User).filter(
            User.email == user_data.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Proveri da li username već postoji
        existing_username = self.db.query(User).filter(
            User.username == user_data.username
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Kreiraj korisnika
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role='form_creator',  # Default role (lowercase za PostgreSQL enum)
            is_active=True,
            is_verified=False  # Treba email verifikacija
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # Generiši tokene
        access_token = create_access_token(data={"sub": str(new_user.id)})
        refresh_token = create_refresh_token(data={"sub": str(new_user.id)})
        
        return UserWithTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(new_user)
        )
    
    def login_user(self, login_data: UserLogin) -> UserWithTokenResponse:
        """
        Autentifikuje korisnika i vraća tokene.
        
        Args:
            login_data: Email i password
        
        Returns:
            UserWithTokenResponse sa tokenima
        
        Raises:
            HTTPException 401: Ako su kredencijali pogrešni
            HTTPException 400: Ako je korisnik neaktivan
        """
        # Pronađi korisnika po emailu
        user = self.db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        # Generiši tokene
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return UserWithTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    
    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generiše novi access token koristeći refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            Novi access i refresh token
        
        Raises:
            HTTPException 401: Ako je refresh token nevažeći
        """
        try:
            payload = decode_token(refresh_token)
            
            # Proveri da li je refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("sub")
            
            # Proveri da li korisnik postoji i aktivan je
            user = self.db.query(User).filter(User.id == int(user_id)).first()
            
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Generiši nove tokene
            new_access_token = create_access_token(data={"sub": str(user.id)})
            new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            )
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
    
    # =========================================================================
    # User Profile Management
    # =========================================================================
    
    def change_password(
        self, 
        user: User, 
        old_password: str, 
        new_password: str
    ) -> bool:
        """
        Menja password korisnika.
        
        Args:
            user: Trenutni korisnik
            old_password: Stari password
            new_password: Novi password
        
        Returns:
            True ako je uspešno
        
        Raises:
            HTTPException 400: Ako je stari password pogrešan
        """
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
        
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        return True
    
    def update_profile(
        self, 
        user: User, 
        full_name: Optional[str] = None,
        username: Optional[str] = None
    ) -> User:
        """
        Ažurira profil korisnika.
        
        Args:
            user: Trenutni korisnik
            full_name: Novo ime (opciono)
            username: Novi username (opciono)
        
        Returns:
            Ažurirani korisnik
        """
        if full_name is not None:
            user.full_name = full_name
        
        if username is not None:
            # Proveri da li je username zauzet
            existing = self.db.query(User).filter(
                User.username == username,
                User.id != user.id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            
            user.username = username
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    # =========================================================================
    # API Key Management
    # =========================================================================
    
    def create_api_key(
        self, 
        user: User, 
        key_data: APIKeyCreate
    ) -> APIKeyCreatedResponse:
        """
        Kreira novi API ključ za korisnika.
        
        Args:
            user: Vlasnik ključa
            key_data: Podaci za kreiranje ključa
        
        Returns:
            Kreiran API ključ (sa samim ključem - prikazuje se samo jednom!)
        """
        # Generiši random API key
        key = f"ff_{token_urlsafe(32)}"
        
        # Izračunaj expiration
        expires_at = None
        if key_data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
        
        api_key = APIKey(
            key=key,
            name=key_data.name,
            user_id=user.id,
            scopes=key_data.scopes,
            expires_at=expires_at
        )
        
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        
        return APIKeyCreatedResponse(
            id=api_key.id,
            key=key,  # Samo ovde se vraća key!
            name=api_key.name,
            scopes=api_key.scopes,
            expires_at=api_key.expires_at
        )
    
    def list_api_keys(self, user: User) -> list[APIKey]:
        """Lista svih API ključeva korisnika."""
        return self.db.query(APIKey).filter(
            APIKey.user_id == user.id
        ).all()
    
    def revoke_api_key(self, user: User, key_id: int) -> bool:
        """
        Deaktivira API ključ.
        
        Args:
            user: Vlasnik ključa
            key_id: ID ključa za deaktivaciju
        
        Returns:
            True ako je uspešno
        
        Raises:
            HTTPException 404: Ako ključ ne postoji
            HTTPException 403: Ako ključ nije vlasništvo korisnika
        """
        api_key = self.db.query(APIKey).filter(APIKey.id == key_id).first()
        
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
        self.db.commit()
        
        return True

