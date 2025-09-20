from typing import List, Optional
from app.domain.models.form import Form
from app.application.interfaces.form_repository import IFormRepository
from app.api.form_schema import FormSchemaCreate

class FormService:
    def __init__(self, form_repo: IFormRepository):
        self.form_repo = form_repo

    def get_form_by_id(self, form_id: int) -> Optional[Form]:
        return self.form_repo.get_by_id(form_id)

    def get_all_forms(self) -> List[Form]:
        return self.form_repo.get_all()

    def create_form(self, form_data: FormSchemaCreate) -> Form:
        return self.form_repo.create(form_data)

    def update_form(self, form_id: int, form_data: FormSchemaCreate) -> Optional[Form]:
        return self.form_repo.update(form_id, form_data)

    def delete_form_by_id(self, form_id: int) -> Optional[Form]:
        return self.form_repo.delete(form_id)
