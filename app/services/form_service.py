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