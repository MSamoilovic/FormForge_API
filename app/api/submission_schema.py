from typing import Any, Dict
from pydantic import BaseModel, ConfigDict


class SubmissionsCreate(BaseModel):
    data: Dict[str, Any]  

class SubmissionResponse(SubmissionsCreate):
    id: int
    submitted_at: str
    form_id: int

    model_config = ConfigDict(from_attributes=True)