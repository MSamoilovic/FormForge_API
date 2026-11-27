from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SubmissionCreate(BaseModel):
    data: dict[str, Any]


class SubmissionResponse(SubmissionCreate):
    id: int
    submitted_at: datetime
    form_id: int

    model_config = ConfigDict(from_attributes=True)
