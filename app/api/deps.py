from fastapi import Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.form_repository import FormRepository
from app.application.services.form_service import FormService
from app.application.interfaces.form_repository import IFormRepository


def get_form_repository(db: Session = Depends(get_db)) -> IFormRepository:
    return FormRepository(db)

def get_form_service(repo: IFormRepository = Depends(get_form_repository)) -> FormService:
    return FormService(repo)
