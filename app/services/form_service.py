from sqlalchemy.orm import Session
from app.schemas.form_schema import FormSchemaCreate
from app.models.form import Form

def create_form(db: Session, form_data: FormSchemaCreate) -> Form: 
    form_dict = form_data.model_dump()
    db_form = Form(**form_dict)
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form