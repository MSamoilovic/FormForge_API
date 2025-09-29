from sqlalchemy.orm import Session
from typing import List, Optional
from app.application.interfaces.form_repository import IFormRepository
from app.domain.models.form import Form
from app.api.form_schema import FormSchemaCreate

class FormRepository(IFormRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, form_id: int) -> Optional[Form]:
        return self.db.query(Form).filter(Form.id == form_id).first()

    def get_all(self) -> list[type[Form]]:
        return self.db.query(Form).all()

    def create(self, form_data: FormSchemaCreate) -> Form:
        db_form = Form(**form_data.model_dump())
        self.db.add(db_form)
        self.db.commit()
        self.db.refresh(db_form)
        return db_form

    def update(self, form_id: int, form_data: FormSchemaCreate) -> Optional[Form]:
        db_form = self.get_by_id(form_id)
        if not db_form:
            return None
        update_data = form_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_form, key, value)
        self.db.add(db_form)
        self.db.commit()
        self.db.refresh(db_form)
        return db_form

    def delete(self, form_id: int) -> Optional[Form]:
        db_form = self.get_by_id(form_id)
        if not db_form:
            return None
        self.db.delete(db_form)
        self.db.commit()
        return db_form
