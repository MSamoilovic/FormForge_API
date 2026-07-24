from typing import List, Optional

from fastapi import HTTPException, status

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

    async def _get_owned_form(self, form_id: int, user_id: int) -> Form:
        """Fetch a form and assert the given user is allowed to modify it.

        Raises 404 if the form does not exist, 403 if it has a different owner.
        Owner-less (anonymous) forms are modifiable by any authenticated user.
        """
        form = await self.form_repo.get_by_id(form_id)
        if form is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
        if form.owner_id and form.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this form"
            )
        return form

    async def update_form(self, form_id: int, form_data: FormSchemaCreate, user_id: int) -> Optional[Form]:
        """Update a form after verifying ownership."""
        await self._get_owned_form(form_id, user_id)
        return await self.form_repo.update(form_id, form_data)

    async def delete_form(self, form_id: int, user_id: int) -> None:
        """Delete a form after verifying ownership."""
        await self._get_owned_form(form_id, user_id)
        await self.form_repo.delete(form_id)
