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
    
    def get_by_form_id(self, form_id):
        return self.session.query(Submission)\
            .filter(Submission.form_id == form_id)\
            .order_by(Submission.submitted_at)\
            .all()

