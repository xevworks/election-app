#!/bin/bash

set -e

echo "=========================================="
echo "Development Mode - Election App Backend"
echo "=========================================="

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done
echo "✓ PostgreSQL is ready!"

echo ""
echo "Running database migrations..."
python manage.py migrate --noinput

echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "Starting Django development server..."
echo "Server will reload on code changes"
echo "=========================================="

exec "$@"
