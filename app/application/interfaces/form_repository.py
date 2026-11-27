from abc import ABC, abstractmethod

from app.api.form_schema import FormSchemaCreate
from app.domain.models.form import Form


class IFormRepository(ABC):
    @abstractmethod
    async def get_by_id(self, form_id: int) -> Form | None:
        pass

    @abstractmethod
    async def get_all(self) -> list[Form]:
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: int) -> list[Form]:
        """Vraća sve forme koje pripadaju određenom korisniku."""

    @abstractmethod
    async def create(
        self, form_data: FormSchemaCreate, owner_id: int | None = None
    ) -> Form:
        """Kreira novu formu"""

    @abstractmethod
    async def update(self, form_id: int, form_data: FormSchemaCreate) -> Form | None:
        """Radi update vec postojece forme"""

    @abstractmethod
    async def delete(self, form_id: int) -> bool:
        """Briše formu i vraća True ako je uspešno, False ako forma ne postoji."""
