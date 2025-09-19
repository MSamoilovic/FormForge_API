from sqlalchemy.orm import Session
from app.schemas.form_schema import FormSchemaCreate
from app.models.form import Form
from typing import List

def create_form(db: Session, form_data: FormSchemaCreate) -> Form: 
    form_dict = form_data.model_dump()
    db_form = Form(**form_dict)
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form

def get_form(db: Session, form_id: int) -> Form | None:
    return db.query(Form).filter(Form.id == form_id).first()

def get_forms(db: Session) -> List[Form]:
    return db.query(Form).all()

def update_form(db: Session, form_id: int, form_data: FormSchemaCreate) -> Form | None:
    """
    Finds and updates an existing form with the provided data.
    """
    db_form = get_form(db, form_id)
    if not db_form:
        return None

    # model_dump() konvertuje Pydantic model u rečnik
    update_data = form_data.model_dump(exclude_unset=True)

    # Prolazimo kroz rečnik i ažuriramo svaki atribut
    for key, value in update_data.items():
        setattr(db_form, key, value)

    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form

def delete_form(db: Session, form_id: int) -> bool:
    db_form = get_form(db, form_id)
    if not db_form:
        return False
    db.delete(db_form)
    db.commit()
    return True