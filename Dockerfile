# Multi-stage build za optimizaciju veličine image-a
FROM python:3.12-slim as base

# Sprečava Python da kreira .pyc fajlove
ENV PYTHONDONTWRITEBYTECODE=1
# Forsira stdout i stderr da budu unbuffered
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instaliraj system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instaliraj Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Kopiraj Poetry konfiguraciju
COPY pyproject.toml poetry.lock ./

# Konfiguriši Poetry da ne kreira virtuelno okruženje (već smo u containeru)
RUN poetry config virtualenvs.create false

# Instaliraj dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Kopiraj aplikaciju
COPY . .

# Kreiraj non-root korisnika za bezbednost
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Ekspoziraj port
EXPOSE 8000

# Entrypoint script će pokrenuti migracije pre pokretanja aplikacije
ENTRYPOINT ["/app/entrypoint.sh"]

# Default komanda za pokretanje aplikacije
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

