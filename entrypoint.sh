#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting FormForge API..."

echo "⏳ Waiting for database to be ready..."
while ! pg_isready -h db -U ${DB_USER:-postgres} > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Database is ready!"

# Pokreni Alembic migracije
echo "🔄 Running database migrations..."
poetry run alembic upgrade head
echo "✅ Migrations completed!"

# Proveri da li treba pokrenuti seed
if [ "$RUN_SEED" = "true" ]; then
    echo "🌱 Running database seed..."
    
    if [ "$CLEAR_DATA" = "true" ]; then
        echo "⚠️  Clearing existing data..."
        poetry run python -m app.database.seed --clear
    else
        poetry run python -m app.database.seed
    fi
    
    echo "✅ Seed completed!"
fi

echo "🎯 Starting application..."
exec "$@"

