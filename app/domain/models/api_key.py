from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class APIKey(Base):
    """Model za API ključeve (programatski pristup)"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)  # Opis za šta se koristi
    
    # Owner
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Permissions
    scopes = Column(JSON, default=["read"])  # read, write, delete
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey {self.name} (user_id={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Proveri da li je ključ istekao"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Proveri da li je ključ validan"""
        return self.is_active and not self.is_expired

