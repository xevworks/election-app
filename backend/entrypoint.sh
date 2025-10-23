#!/bin/bash

set -e

echo "=========================================="
echo "Starting Election App Backend"
echo "=========================================="

echo "Waiting for PostgreSQL..."
max_retries=30
counter=0

while ! nc -z db 5432; do
  counter=$((counter+1))
  if [ $counter -gt $max_retries ]; then
    echo "ERROR: PostgreSQL did not start in time"
    exit 1
  fi
  echo "Waiting for PostgreSQL... ($counter/$max_retries)"
  sleep 1
done

echo "✓ PostgreSQL is ready!"

echo ""
echo "Running database migrations..."
python manage.py migrate --noinput || {
  echo "ERROR: Migration failed"
  exit 1
}
echo "✓ Migrations completed"

echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput || {
  echo "ERROR: Collectstatic failed"
  exit 1
}
echo "✓ Static files collected"

echo ""
echo "=========================================="
echo "Starting Gunicorn server..."
echo "=========================================="
exec gunicorn \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --threads 4 \
  --worker-class gthread \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  backend.wsgi:application
