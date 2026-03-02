#!/usr/bin/env bash
# Pokretanje svih servisa u Dockeru
set -e

docker compose up -d --build

echo "Svi servisi su pokrenuti."
echo "  API        : http://localhost:${API_PORT:-8000}"
echo "  PostgreSQL : localhost:${DB_PORT:-5432}"
echo "  pgAdmin    : http://localhost:${PGADMIN_PORT:-5050}"
