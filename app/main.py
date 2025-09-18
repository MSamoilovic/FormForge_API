from typing import List
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.schemas.form_schema import FormSchemaCreate, FormSchemaResponse
from app.services import form_service
from app.db.session import get_db, engine
from app.db import base

base.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FormForge API")

origins = ["http://localhost:4500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.post("/api/forms", response_model=FormSchemaResponse, status_code=201)
def create_form_endpoint(form: FormSchemaCreate, db: Session = Depends(get_db)):
    print(f"--- Saving form '{form.name}' to the database ---")
    created_form = form_service.create_form(db, form_data=form)
    return created_form


@app.get("/api/forms", response_model=List[FormSchemaResponse], status_code=200)
def get_all_forms(db: Session = Depends(get_db)):
    return form_service.get_forms(db=db)


@app.get("/api/forms/{form_id}",response_model=FormSchemaResponse, status_code=200)
def get_form_by_id(form_id: int, db: Session = Depends(get_db)):
    form = form_service.get_form(db, form_id=form_id)
    return form


