#!/usr/bin/env bash
# Pokretanje samo baze i pgAdmin (za lokalni razvoj)
set -e

docker compose up -d db pgadmin

echo "Baza i pgAdmin su pokrenuti."
echo "  PostgreSQL : localhost:${DB_PORT:-5432}"
echo "  pgAdmin    : http://localhost:${PGADMIN_PORT:-5050}"
