#!/usr/bin/env bash
# Pokretanje svih servisa u Dockeru
set -e

docker compose up -d --build

echo "Svi servisi su pokrenuti."
echo "  API        : http://localhost:${API_PORT:-8000}"
echo "  PostgreSQL : samo unutar Docker mreže (db:5432), bez trajnog volume-a"
