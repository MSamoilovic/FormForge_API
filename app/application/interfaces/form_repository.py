from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.form import Form
from app.api.form_schema import FormSchemaCreate # Importovaćemo ga kasnije

class IFormRepository(ABC):
    @abstractmethod
    def get_by_id(self, form_id: int) -> Optional[Form]:
        pass

    @abstractmethod
    def get_all(self) -> List[Form]:
        pass

    @abstractmethod
    def create(self, form_data: FormSchemaCreate) -> Form:
        pass

    @abstractmethod
    def update(self, form_id: int, form_data: FormSchemaCreate) -> Optional[Form]:
        pass

    @abstractmethod
    def delete(self, form_id: int) -> Optional[Form]:
        pass
