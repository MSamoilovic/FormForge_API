import csv
import io
from typing import List, Dict, Any, Iterable, Sequence
from app.api.submission_schema import SubmissionCreate
from app.application.interfaces.submission_repository import ISubmissionRepository
from app.domain.models.submission import Submission


class SubmissionService:
    def __init__(self, submission_repository: ISubmissionRepository):
        self.submission_repository = submission_repository

    async def create_submission(self, form_id: int, submission_data: SubmissionCreate) -> Submission:
        return await self.submission_repository.create(form_id, submission_data)

    async def get_submissions_by_form_id(self, form_id: int, filters: Dict[str, Any] = None) -> List[type[Submission]]:
        return await self.submission_repository.get_all_by_form_id(form_id, filters)

    @staticmethod
    def to_csv(submissions: Sequence[Submission], field_ids: Iterable[str]) -> str:
        """Render submissions as a CSV string.

        Columns are driven by the form's field ids (stable order), so fields
        that happen to be absent from the first submission are not dropped.
        Any extra keys present in the data but not in the form definition are
        appended after the known columns.
        """
        columns: List[str] = list(field_ids)
        seen = set(columns)
        for submission in submissions:
            for key in submission.data.keys():
                if key not in seen:
                    seen.add(key)
                    columns.append(key)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "submitted_at"] + columns)
        for submission in submissions:
            writer.writerow(
                [submission.id, submission.submitted_at]
                + [submission.data.get(col, "") for col in columns]
            )
        output.seek(0)
        return output.getvalue()
