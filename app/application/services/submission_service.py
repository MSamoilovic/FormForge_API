from typing import List
from app.api.submission_schema import SubmissionsCreate
from app.application.interfaces.submission_repository import ISubmissionRepository
from app.domain.models.submission import Submission


class SubmissionService:
    def __init__(self, submission_repository: ISubmissionRepository):
        self.submission_repository = submission_repository

    async def create_submission(self, form_id: int, submission_data: SubmissionsCreate) -> Submission:
        return await self.submission_repository.create_submission(form_id, submission_data)
    
    async def get_submissions_by_form_id(self, form_id: int) -> List[Submission]:
        return await self.submission_repository.get_by_form_id(form_id)