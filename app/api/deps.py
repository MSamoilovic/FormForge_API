from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.submission_repository import ISubmissionRepository
from app.infrastructure.repositories.submission_repository import SubmissionRepository
from app.application.services.submission_service import SubmissionService
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.form_repository import FormRepository
from app.application.services.form_service import FormService
from app.application.interfaces.form_repository import IFormRepository
from app.application.interfaces.user_repository import IUserRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.application.services.auth_service import AuthService


def get_form_repository(db: AsyncSession = Depends(get_db)) -> IFormRepository:
    return FormRepository(db)

def get_form_service(repo: IFormRepository = Depends(get_form_repository)) -> FormService:
    return FormService(repo)

def get_submission_repository(db: AsyncSession = Depends(get_db)) -> ISubmissionRepository:
    return SubmissionRepository(db_session=db)

def get_submission_service(repo: ISubmissionRepository = Depends(get_submission_repository)) -> SubmissionService:
    return SubmissionService(repo)

def get_user_repository(db: AsyncSession = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)

def get_auth_service(repo: IUserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)
