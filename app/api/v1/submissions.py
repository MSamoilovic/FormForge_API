from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from app.application.services.submission_service import SubmissionService
from app.application.services.form_service import FormService
from app.api.deps import get_submission_service, get_form_service
from app.api.submission_schema import SubmissionCreate

from app.api.submission_schema import SubmissionResponse


router = APIRouter()

@router.post("/{form_id}/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission_for_form(
    form_id: int,
    submission: SubmissionCreate,
    service: SubmissionService = Depends(get_submission_service),
    form_service: FormService = Depends(get_form_service)
):
    db_form = form_service.get_form_by_id(form_id)
    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")
        
    return service.create_submission(form_id=form_id, submission_data=submission)

@router.get("/{form_id}", response_model=List[SubmissionResponse])
def read_submissions_for_form(
    form_id: int,
    service: SubmissionService = Depends(get_submission_service)
):
    
    return service.get_submissions_by_form_id(form_id)