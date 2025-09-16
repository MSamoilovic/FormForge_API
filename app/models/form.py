from sqlalchemy import Column, String, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    
    fields = Column(JSON, nullable=False)
    rules = Column(JSON, nullable=True)
