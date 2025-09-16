from typing import List
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Uvozimo sve što nam treba iz naših modula
from app.schemas.form_schema import FormSchemaCreate, FormaSchemaResponse, FormSchema
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

@app.get("/api/hello")
def read_root():
    """ Test endpoint da proverimo da li server radi. """
    return {"message": "Hello from FormForge API!"}


@app.post("/api/forms", response_model=FormaSchemaResponse, status_code=201)
def create_form_endpoint(form: FormSchemaCreate, db: Session = Depends(get_db)):
    """
    Prima novu FormSchema, prosleđuje je servisnom sloju da je sačuva u bazu,
    i vraća je nazad kao potvrdu.
    `db: Session = Depends(get_db)` je magija FastAPI-ja koja nam daje
    svežu konekciju ka bazi za svaki zahtev.
    """
    print(f"--- Saving form '{form.name}' to the database ---")
    created_form = form_service.create_form(db, form_data=form)
    return created_form


@app.get("/api/forms", response_model=List[FormSchema])
def get_all_forms():
    """ Vraća listu svih sačuvanih formi. """
    return db["forms"]

