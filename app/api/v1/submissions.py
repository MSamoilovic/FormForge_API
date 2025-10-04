import csv
import io
from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import StreamingResponse

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

@router.get("/{form_id}/export", response_class=StreamingResponse)
async def export_form_submissions(
    form_id: int,
    request: Request,
    service: SubmissionService = Depends(get_submission_service)
):
    filters = dict(request.query_params)

    submissions = await service.get_submissions_by_form_id(form_id=form_id, filters=filters)

    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found for the given criteria.")

    output = io.StringIO()
    writer = csv.writer(output)

    first_submission_data = submissions[0].data
    header = ['id', 'submitted_at'] + list(first_submission_data.keys())
    writer.writerow(header)

    for submission in submissions:
        row = [submission.id, submission.submitted_at] + [submission.data.get(key, '') for key in first_submission_data.keys()]
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=form_{form_id}_submissions.csv"}
    )