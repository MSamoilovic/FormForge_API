from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.api.submission_schema import SubmissionCreate
from app.domain.models.submission import Submission


class ISubmissionRepository(ABC):
   
    @abstractmethod
    def create(self, form_id: int, submission_data: SubmissionCreate) -> Submission:
        pass

    @abstractmethod
    async def get_all_by_form_id(self, form_id: int, filters: Dict[str, Any] = None) -> List[type[Submission]]:
        pass

    @abstractmethod
    def get_by_id(self, submission_id: int) -> Optional[Submission]:
        pass

    @abstractmethod
    def update(self, submission_id: int, submission_data: SubmissionCreate) -> Optional[Submission]:
        pass

    @abstractmethod
    def delete(self, submission_id: int) -> Optional[Submission]:
        pass
