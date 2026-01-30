from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base


class UserRole(str, enum.Enum):
    """Korisničke role za RBAC"""
    SUPER_ADMIN = "super_admin"      # Potpuna kontrola sistema
    ORG_ADMIN = "org_admin"          # Admin organizacije
    FORM_CREATOR = "form_creator"    # Može kreirati forme
    VIEWER = "viewer"                # Read-only pristup


class User(Base):
    """Model za korisnike sistema"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Role
    role = Column(Enum(UserRole), default=UserRole.FORM_CREATOR)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Multi-tenancy - opciono
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Relations
    organization = relationship("Organization", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    forms = relationship("Form", back_populates="owner")

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"

