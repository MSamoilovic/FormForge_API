from fastapi import FastAPI, Body
from typing import List

from  app.schemas.form_schema import FormSchema, FormSchemaCreate

db = {
    "forms": [],
}

app = FastAPI(
    title="FormForge API",
    description="Backend API for the FormForge dynamic form builder.",
    version="0.1.0",
)




@app.post("/api/forms", response_model=FormSchema, status_code=201)
def create_form(form_data: FormSchemaCreate = Body(...)):
    """
    Prima JSON sa podacima o novoj formi, validira ga i "čuva".
    """
    new_form_dict = form_data.model_dump()
    new_form_dict["id"] = f"form_{len(db['forms']) + 1}"
    new_form = FormSchema(**new_form_dict)
    db["forms"].append(new_form)
    print(f"Form saved: {new_form.name}")
    return new_form

@app.get("/api/forms", response_model=List[FormSchema])
def get_all_forms():
    """ Vraća listu svih sačuvanih formi. """
    return db["forms"]

