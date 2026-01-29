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

# Instaliraj uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Kopiraj uv konfiguraciju
COPY pyproject.toml uv.lock* ./

# Instaliraj dependencies (uv sync instalira sve iz uv.lock)
RUN uv sync --frozen --no-dev --no-install-project

# Kopiraj aplikaciju
COPY . .

# Instaliraj projekat
RUN uv sync --frozen --no-dev

# Kreiraj non-root korisnika za bezbednost
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Ekspoziraj port
EXPOSE 8000

# Entrypoint script će pokrenuti migracije pre pokretanja aplikacije
ENTRYPOINT ["/app/entrypoint.sh"]

# Default komanda za pokretanje aplikacije
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
