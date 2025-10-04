from typing import List, Dict, Any
from app.api.submission_schema import SubmissionCreate
from app.application.interfaces.submission_repository import ISubmissionRepository
from app.domain.models.submission import Submission


class SubmissionService:
    def __init__(self, submission_repository: ISubmissionRepository):
        self.submission_repository = submission_repository

    def create_submission(self, form_id: int, submission_data: SubmissionCreate) -> Submission:
        return  self.submission_repository.create(form_id, submission_data)
    
    async def get_submissions_by_form_id(self, form_id: int, filters: Dict[str, Any] = None) -> List[type[Submission]]:
        return  await self.submission_repository.get_all_by_form_id(form_id)