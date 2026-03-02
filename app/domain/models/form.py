from sqlalchemy import Column, String, JSON, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Form(Base):
    __tablename__ = "forms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    fields = Column(JSON, nullable=False)
    rules = Column(JSON, nullable=True, default=[])
    theme = Column(JSON, nullable=True)
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relations
    submissions = relationship("Submission", back_populates="form")
    owner = relationship("User", back_populates="forms")
    organization = relationship("Organization", back_populates="forms")

