from typing import Any, Dict
from pydantic import BaseModel, ConfigDict


class SubmissionCreate(BaseModel):
    data: Dict[str, Any]  

class SubmissionResponse(SubmissionCreate):
    id: int
    submitted_at: str
    form_id: int

    model_config = ConfigDict(from_attributes=True)