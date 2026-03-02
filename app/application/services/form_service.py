from typing import List, Optional
from app.domain.models.form import Form
from app.application.interfaces.form_repository import IFormRepository
from app.api.form_schema import FormSchemaCreate


class FormService:
    def __init__(self, form_repo: IFormRepository):
        self.form_repo = form_repo

    async def get_form_by_id(self, form_id: int) -> Optional[Form]:
        return await self.form_repo.get_by_id(form_id)

    async def get_all_forms(self) -> List[Form]:
        return await self.form_repo.get_all()

    async def get_forms_by_owner(self, owner_id: int) -> List[Form]:
        """Vraća sve forme koje pripadaju određenom korisniku."""
        return await self.form_repo.get_by_owner(owner_id)

    async def create_form(self, form_data: FormSchemaCreate, owner_id: Optional[int] = None) -> Form:
        """Kreira novu formu, opciono sa owner_id."""
        return await self.form_repo.create(form_data, owner_id=owner_id)

    async def update_form(self, form_id: int, form_data: FormSchemaCreate) -> Optional[Form]:
        return await self.form_repo.update(form_id, form_data)

    async def delete_form(self, form_id: int) -> bool:
        """Briše formu i vraća True ako je uspešno."""
        return await self.form_repo.delete(form_id)
