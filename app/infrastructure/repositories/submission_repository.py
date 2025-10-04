from typing import Dict, Any, List, Optional

from app.api.submission_schema import SubmissionCreate
from app.application.interfaces.submission_repository import ISubmissionRepository
from app.domain.models.submission import Submission
from sqlalchemy.orm import Session


class SubmissionRepository(ISubmissionRepository):
    def __init__(self, db_session: Session):
        self.session = db_session

    def create(self, form_id: int, submission_data: SubmissionCreate) -> Submission:
        
        db_submission = Submission(
            form_id=form_id,
            data = submission_data.data
        )

        self.session.add(db_submission)
        self.session.commit()
        self.session.refresh(db_submission)
        return db_submission

    async def get_all_by_form_id(self, form_id: int, filters: Dict[str, Any] = None) -> List[type[Submission]]:

        query = self.session.query(Submission).filter(Submission.form_id == form_id)

        if filters:
            for key, value in filters.items():
                if value:
                    query = query.filter(Submission.data[key].astext().ilike(f"%{value}%"))

        return query.order_by(Submission.submitted_at.desc()).all()

    def get_by_id(self, submission_id: int) -> Optional[Submission]:
        pass

    def update(self, submission_id: int, submission_data: Submission) -> Optional[Submission]:
        pass

    def delete(self, submission_id: int) -> Optional[Submission]:
        pass
