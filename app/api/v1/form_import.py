"""
API endpoints za import formi iz Excel fajlova.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from app.application.services.excel_import_service import ExcelImportService
from app.api.form_schema import FormSchemaCreate
from app.core.security import get_current_user
from app.domain.models.user import User


router = APIRouter(prefix="/forms/import", tags=["Form Import"])


# =============================================================================
# Response Schemas
# =============================================================================

class ImportSuccessResponse(BaseModel):
    """Response kada je import uspešan."""
    success: bool = True
    message: str = "Excel parsed successfully"
    form: FormSchemaCreate


class ImportErrorResponse(BaseModel):
    """Response kada import ima greške."""
    success: bool = False
    message: str = "Validation errors found"
    errors: List[str]


# =============================================================================
# Endpoints
# =============================================================================

@router.get(
    "/template",
    summary="Download Excel template",
    description="Download empty Excel template for form import.",
    response_class=StreamingResponse
)
async def download_template():
    """
    Preuzimanje praznog Excel template-a za import formi.
    
    Template sadrži:
    - **Form** sheet: name, description
    - **Fields** sheet: id, label, type, placeholder, required, options, min, max
    - **Instructions** sheet: Uputstvo za popunjavanje
    
    Primer podataka je uključen u template.
    """
    service = ExcelImportService()
    excel_file = service.generate_template()
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=formforge_template.xlsx"
        }
    )


@router.post(
    "/excel",
    summary="Import form from Excel",
    description="Upload Excel file and parse it into form schema.",
    responses={
        200: {"model": ImportSuccessResponse, "description": "Excel parsed successfully"},
        400: {"model": ImportErrorResponse, "description": "Validation errors"},
    }
)
async def import_from_excel(
    file: UploadFile = File(..., description="Excel file (.xlsx)"),
    current_user: User = Depends(get_current_user)
):
    """
    Import forme iz Excel fajla.
    
    **Zahteva autentifikaciju.**
    
    Excel fajl mora sadržati:
    - **Form** sheet sa kolonama: name, description
    - **Fields** sheet sa kolonama: id, label, type, placeholder, required, options, min, max
    
    Vraća JSON koji može direktno da se koristi za kreiranje forme.
    
    **Validacije:**
    - Form name je obavezan
    - Svako polje mora imati id, label i type
    - Field ID mora biti jedinstven
    - Select/radio tipovi zahtevaju options
    - Number tipovi zahtevaju min i max
    """
    # Provera file tipa
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only .xlsx files are supported."
        )
    
    # Čitanje fajla
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Parsiranje
    service = ExcelImportService()
    success, form_schema, errors = service.parse_excel(content)
    
    if not success:
        return ImportErrorResponse(
            success=False,
            message="Validation errors found",
            errors=errors
        )
    
    return ImportSuccessResponse(
        success=True,
        message="Excel parsed successfully. Use this data to create the form.",
        form=form_schema
    )


@router.post(
    "/excel/preview",
    summary="Preview form from Excel (no auth)",
    description="Upload Excel file and preview the form schema without authentication.",
    responses={
        200: {"model": ImportSuccessResponse, "description": "Excel parsed successfully"},
        400: {"model": ImportErrorResponse, "description": "Validation errors"},
    }
)
async def preview_from_excel(
    file: UploadFile = File(..., description="Excel file (.xlsx)")
):
    """
    Preview forme iz Excel fajla (bez autentifikacije).
    
    Isti kao /excel endpoint ali ne zahteva login.
    Koristan za testiranje pre registracije.
    """
    # Provera file tipa
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only .xlsx files are supported."
        )
    
    # Čitanje fajla
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Parsiranje
    service = ExcelImportService()
    success, form_schema, errors = service.parse_excel(content)
    
    if not success:
        return ImportErrorResponse(
            success=False,
            message="Validation errors found",
            errors=errors
        )
    
    return ImportSuccessResponse(
        success=True,
        message="Excel parsed successfully. Use this data to create the form.",
        form=form_schema
    )
