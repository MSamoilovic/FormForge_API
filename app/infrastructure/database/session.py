from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DB_ECHO)

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """
    Dependency Injection funkcija. FastAPI će je pozvati za svaki zahtev.
    Ona otvara novu sesiju ka bazi, daje je endpointu da je koristi,
    i na kraju je uvek zatvara, čak i ako dođe do greške.
    """
    async with SessionLocal() as session:
        yield session