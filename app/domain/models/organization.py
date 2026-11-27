from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Organization(Base, TimestampMixin):
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

    # Relations
    users = relationship("User", back_populates="organization")
    forms = relationship("Form", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name} ({self.slug})>"
