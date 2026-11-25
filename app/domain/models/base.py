from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

from app.core.time import utcnow

Base = declarative_base()


class TimestampMixin:
    """Adds `created_at` / `updated_at` columns.

    Mixed into models that carry both timestamps (Form, User, Organization).
    Models with a different shape (APIKey has only `created_at`, Submission
    uses `submitted_at`) keep their own columns.
    """
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, onupdate=utcnow)
