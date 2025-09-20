from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.application.services.form_service import FormService
from app.api.form_schema import FormSchemaCreate, FormSchemaResponse
from app.api.deps import get_form_service

router = APIRouter()

@router.post("/", response_model=FormSchemaResponse, status_code=status.HTTP_201_CREATED)
def create_form(form: FormSchemaCreate, service: FormService = Depends(get_form_service)):
    return service.create_form(form)

@router.get("/", response_model=List[FormSchemaResponse])
def read_forms(service: FormService = Depends(get_form_service)):
    return service.get_all_forms()

@router.get("/{form_id}", response_model=FormSchemaResponse)
def read_form(form_id: int, service: FormService = Depends(get_form_service)):
    db_form = service.get_form_by_id(form_id)
    if db_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return db_form


@router.put("/api/forms/{form_id}", response_model=FormSchemaResponse, status_code=200)
def update_form_endpoint(form_id: int, form: FormSchemaCreate, service: FormService = Depends(get_form_service)):
    """ Updates an existing form with the provided data. """
    updated_form = service.update_form(form_id=form_id, form_data=form)
    if updated_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return updated_form

@router.delete("/api/forms/{form_id}", status_code=204)
def delete_form_endpoint(form_id: int, service: FormService = Depends(get_form_service)):
    """ Deletes the form with the provided id. """
    success = service.delete_form(form_id=form_id)
    if not success:
        raise HTTPException(status_code=404, detail="Form not found")
    return success
