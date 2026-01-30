from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Organization(Base):
    """Model za organizacije (multi-tenancy podrška)"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    
    # Subscription info
    plan = Column(String, default="free")  # free, pro, enterprise
    max_forms = Column(Integer, default=10)
    max_submissions_per_month = Column(Integer, default=1000)
    
    # Settings
    settings = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relations
    users = relationship("User", back_populates="organization")
    forms = relationship("Form", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name} ({self.slug})>"

