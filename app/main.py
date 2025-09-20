from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.forms import router as form_routes


from app.domain.models.form import Base
from app.infrastructure.database.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FormForge API")

# --- CORS Middleware ---
# Omogućava našoj Angular aplikaciji da komunicira sa ovim backend-om
origins = [
    "http://localhost:4500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(form_routes, prefix="/api/forms", tags=["Forms"])


@app.get("/api/health")
def read_root():
    """ Proverava da li je API živ. """
    return {"status": "ok"}