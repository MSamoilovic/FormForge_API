from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.forms import router as form_routes
from app.api.v1.submissions import router as submission_routes
from app.api.v1.ai import router as ai_routes
from app.api.v1.auth import router as auth_routes

from app.domain.models.base import Base
from app.infrastructure.database.session import engine


app = FastAPI(
    title="FormForge API",
    description="Dynamic form builder API with AI integration and authentication",
    version="1.0.0"
)

# --- CORS Middleware ---
origins = [
    "http://localhost:4200",  # Angular default port
    "http://127.0.0.1:4200",
    "http://localhost:4500",
    "http://localhost:8001",
    "http://127.0.0.1:4500",
    "http://127.0.0.1:8001",
    "http://localhost:3000",  # Common React dev port
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)


app.include_router(auth_routes, prefix="/api")
app.include_router(form_routes, prefix="/api/forms", tags=["Forms"])
app.include_router(submission_routes, prefix="/api/submissions", tags=["Submissions"])
app.include_router(ai_routes, prefix="/api/ai", tags=["AI"])

# Add explicit routes without trailing slash to avoid redirects that break CORS
from typing import List
from app.api.form_schema import FormSchemaResponse
from app.api.deps import get_form_service
from app.application.services.form_service import FormService
from fastapi import Depends

@app.get("/api/forms", response_model=List[FormSchemaResponse], include_in_schema=False)
def read_forms_no_slash(service: FormService = Depends(get_form_service)):
    """Handle /api/forms without trailing slash to avoid CORS issues with redirects"""
    return service.get_all_forms()


@app.get("/api/health")
def read_root():
    """ Proverava da li je API živ. """
    return {"status": "ok"}