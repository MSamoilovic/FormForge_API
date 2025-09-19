from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Uvozimo ispravne modele
from app.schemas.form_schema import FormSchemaCreate, FormSchemaResponse
from .services import form_service
from .db.session import get_db, engine
from .db import base

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
    """ Creates a new form and saves it in the database. """
    created_form = form_service.create_form(db, form_data=form)
    return created_form


@app.get("/api/forms", response_model=List[FormSchemaResponse])
def get_forms_endpoint(db: Session = Depends(get_db)):
    """ Returns the list of all available forms. """
    forms = form_service.get_forms(db=db)
    return forms


@app.get("/api/forms/{form_id}", response_model=FormSchemaResponse)
def get_form_endpoint(form_id: int, db: Session = Depends(get_db)):
    """ Returns Form with provided id. """
    db_form = form_service.get_form(db=db, form_id=form_id)
    if db_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return db_form

@app.put("/api/forms/{form_id}", response_model=FormSchemaResponse, status_code=200)
def update_form_endpoint(form_id: int, form: FormSchemaCreate, db: Session = Depends(get_db)):
    """ Updates an existing form with the provided data. """
    updated_form = form_service.update_form(db=db, form_id=form_id, form_data=form)
    if updated_form is None:
        raise HTTPException(status_code=404, detail="Form not found")
    return updated_form

@app.delete("/api/forms/{form_id}", status_code=204)
def delete_form_endpoint(form_id: int, db: Session = Depends(get_db)):
    """ Deletes the form with the provided id. """
    success = form_service.delete_form(db=db, form_id=form_id)
    if not success:
        raise HTTPException(status_code=404, detail="Form not found")
    return success
