from typing import Any, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SubmissionCreate(BaseModel):
    data: Dict[str, Any]  

class SubmissionResponse(SubmissionCreate):
    id: int
    submitted_at: datetime
    form_id: int

    model_config = ConfigDict(from_attributes=True)