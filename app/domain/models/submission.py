from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .form import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    data = Column(JSON, nullable=False)

    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    form = relationship("Form", back_populates="submissions")
    