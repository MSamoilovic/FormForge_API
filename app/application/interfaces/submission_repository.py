from abc import ABC, abstractmethod
from typing import Any

from app.api.submission_schema import SubmissionCreate
from app.domain.models.submission import Submission


class ISubmissionRepository(ABC):
    @abstractmethod
    async def create(
        self, form_id: int, submission_data: SubmissionCreate
    ) -> Submission:
        pass

    @abstractmethod
    async def get_all_by_form_id(
        self, form_id: int, filters: dict[str, Any] = None
    ) -> list[type[Submission]]:
        pass

    @abstractmethod
    async def get_by_id(self, submission_id: int) -> Submission | None:
        pass

    @abstractmethod
    async def update(
        self, submission_id: int, submission_data: SubmissionCreate
    ) -> Submission | None:
        pass

    @abstractmethod
    async def delete(self, submission_id: int) -> Submission | None:
        pass
