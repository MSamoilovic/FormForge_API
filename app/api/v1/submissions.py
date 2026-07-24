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
from app.core.security import require_scope
from app.domain.models.user import User

from app.api.submission_schema import SubmissionResponse


router = APIRouter()


def _ensure_can_read_submissions(db_form, user: User) -> None:
    """Only the form's owner may read its submissions.

    Anonymous forms (no owner) are readable by any authenticated caller,
    since there is no owner to scope them to.
    """
    if db_form.owner_id and db_form.owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this form's submissions"
        )

@router.post("/{form_id}/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission_for_form(
    form_id: int,
    submission: SubmissionCreate,
    service: SubmissionService = Depends(get_submission_service),
    form_service: FormService = Depends(get_form_service)
):
    db_form = await form_service.get_form_by_id(form_id)
    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")

    return await service.create_submission(form_id=form_id, submission_data=submission)

@router.get("/{form_id}", response_model=List[SubmissionResponse])
async def read_submissions_for_form(
    form_id: int,
    service: SubmissionService = Depends(get_submission_service),
    form_service: FormService = Depends(get_form_service),
    current_user: User = Depends(require_scope("read"))
):
    db_form = await form_service.get_form_by_id(form_id)
    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")
    _ensure_can_read_submissions(db_form, current_user)

    return await service.get_submissions_by_form_id(form_id)

@router.get("/{form_id}/export", response_class=StreamingResponse)
async def export_form_submissions(
    form_id: int,
    request: Request,
    service: SubmissionService = Depends(get_submission_service),
    form_service: FormService = Depends(get_form_service),
    current_user: User = Depends(require_scope("read"))
):
    db_form = await form_service.get_form_by_id(form_id)
    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")
    _ensure_can_read_submissions(db_form, current_user)

    # Only accept filters that name an actual field of this form. Any other
    # query param is ignored, so arbitrary keys can't be injected into the
    # JSON lookup.
    allowed_keys = {field["id"] for field in (db_form.fields or []) if "id" in field}
    filters = {
        key: value
        for key, value in request.query_params.items()
        if key in allowed_keys
    }

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