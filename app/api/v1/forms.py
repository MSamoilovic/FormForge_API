from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.application.services.form_service import FormService
from app.api.form_schema import FormSchemaCreate, FormSchemaResponse
from app.api.deps import get_form_service
from app.core.security import get_current_user_optional, require_scope
from app.domain.models.user import User

router = APIRouter()


@router.post("", response_model=FormSchemaResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=FormSchemaResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_form(
    form: FormSchemaCreate,
    service: FormService = Depends(get_form_service),
    current_user: User = Depends(require_scope("write"))
):
    """
    Kreira novu formu.

    Zahteva autentifikaciju (JWT ili API ključ sa 'write' scope-om) -
    forma će biti vezana za korisnika koji je kreira.
    """
    return await service.create_form(form, owner_id=current_user.id)


@router.get("", response_model=List[FormSchemaResponse])
@router.get("/", response_model=List[FormSchemaResponse], include_in_schema=False)
async def read_forms(
    service: FormService = Depends(get_form_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Vraća listu svih formi.
    
    Ako je korisnik ulogovan, vraća samo njegove forme.
    Ako nije, vraća sve javne forme.
    """
    if current_user:
        return await service.get_forms_by_owner(current_user.id)
    return await service.get_all_forms()


@router.get("/{form_id}", response_model=FormSchemaResponse)
async def read_form(
    form_id: int, 
    service: FormService = Depends(get_form_service)
):
    """
    Vraća formu po ID-u.
    
    Forme su javno dostupne za čitanje (potrebno za popunjavanje).
    """
    db_form = await service.get_form_by_id(form_id)
    if db_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return db_form


@router.put("/{form_id}", response_model=FormSchemaResponse, status_code=200)
async def update_form(
    form_id: int, 
    form: FormSchemaCreate, 
    service: FormService = Depends(get_form_service),
    current_user: User = Depends(require_scope("write"))
):
    """
    Ažurira postojeću formu.

    Zahteva autentifikaciju (JWT ili API ključ sa 'write' scope-om) -
    samo vlasnik forme može da je ažurira.
    """
    # Proveri ownership
    existing_form = await service.get_form_by_id(form_id)
    if existing_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    
    if existing_form.owner_id and existing_form.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this form")
    
    updated_form = await service.update_form(form_id=form_id, form_data=form)
    return updated_form


@router.delete("/{form_id}", status_code=204)
async def delete_form_endpoint(
    form_id: int, 
    service: FormService = Depends(get_form_service),
    current_user: User = Depends(require_scope("delete"))
):
    """
    Briše formu.

    Zahteva autentifikaciju (JWT ili API ključ sa 'delete' scope-om) -
    samo vlasnik forme može da je obriše.
    """
    # Proveri ownership
    existing_form = await service.get_form_by_id(form_id)
    if existing_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    
    if existing_form.owner_id and existing_form.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this form")
    
    success = await service.delete_form(form_id=form_id)
    if not success:
        raise HTTPException(status_code=404, detail="Form not found")
    return None
