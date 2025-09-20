from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency Injection funkcija. FastAPI će je pozvati za svaki zahtev.
    Ona otvara novu sesiju ka bazi, daje je endpointu da je koristi,
    i na kraju je uvek zatvara, čak i ako dođe do greške.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()