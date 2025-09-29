from fastapi import Depends
from sqlalchemy.orm import Session
from app.application.interfaces.submission_repository import ISubmissionRepository
from app.infrastructure.repositories.submission_repository import SubmissionRepository
from app.application.services.submission_service import SubmissionService
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.form_repository import FormRepository
from app.application.services.form_service import FormService
from app.application.interfaces.form_repository import IFormRepository


def get_form_repository(db: Session = Depends(get_db)) -> IFormRepository:
    return FormRepository(db)

def get_form_service(repo: IFormRepository = Depends(get_form_repository)) -> FormService:
    return FormService(repo)

def get_submission_repository(db: Session = Depends(get_db)) -> ISubmissionRepository:
    return SubmissionRepository(db_session=db)

def get_submission_service(repo: ISubmissionRepository = Depends(get_submission_repository)) -> SubmissionService:
    return SubmissionService(repo)
