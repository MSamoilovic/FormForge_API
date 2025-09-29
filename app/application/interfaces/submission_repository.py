from abc import ABC, abstractmethod
from typing import List


from app.api.submission_schema import SubmissionCreate
from app.domain.models.submission import Submission


class ISubmissionRepository(ABC):
   
    @abstractmethod
    def create(self, form_id: int, submission_data: SubmissionCreate) -> Submission:
        pass

    @abstractmethod
    def get_by_form_id(self, form_id: int) -> List[Submission]:
        pass