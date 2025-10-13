from sqlalchemy import Column, String, JSON, Integer
from sqlalchemy.orm import declarative_base, relationship
from .base import Base


class Form(Base):
    __tablename__ = "forms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    fields = Column(JSON, nullable=False)
    rules = Column(JSON, nullable=True, default=[])
    theme = Column(JSON, nullable=True)
    submissions = relationship("Submission", back_populates="form")

