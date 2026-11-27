
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.form_schema import FormSchemaCreate
from app.application.interfaces.form_repository import IFormRepository
from app.domain.models.form import Form


class FormRepository(IFormRepository):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_by_id(self, form_id: int) -> Form | None:
        result = await self.db.execute(select(Form).filter(Form.id == form_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Form]:
        result = await self.db.execute(select(Form))
        return result.scalars().all()

    async def get_by_owner(self, owner_id: int) -> list[Form]:
        """Vraća sve forme koje pripadaju određenom korisniku."""
        # return self.db.query(Form).filter(Form.owner_id == owner_id).all()
        result = await self.db.execute(select(Form).filter(Form.owner_id == owner_id))
        return result.scalars().all()

    async def create(
        self, form_data: FormSchemaCreate, owner_id: int | None = None
    ) -> Form:
        db_form = Form(**form_data.model_dump(), owner_id=owner_id)
        self.db.add(db_form)
        await self.db.commit()
        await self.db.refresh(db_form)
        return db_form

    async def update(self, form_id: int, form_data: FormSchemaCreate) -> Form | None:
        db_form = await self.get_by_id(form_id)
        if not db_form:
            return None
        update_data = form_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_form, key, value)
        self.db.add(db_form)
        await self.db.commit()
        await self.db.refresh(db_form)
        return db_form

    async def delete(self, form_id: int) -> bool:
        """Briše formu i vraća True ako je uspešno."""
        db_form = await self.get_by_id(form_id)
        if not db_form:
            return False
        await self.db.delete(db_form)
        await self.db.commit()
        return True
