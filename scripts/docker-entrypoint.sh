#!/bin/sh
set -e

echo "Waiting for database..."
for i in $(seq 1 30); do
  if python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
" 2>/dev/null; then
    echo "Database is ready."
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "Database not available after 30s" >&2
    exit 1
  fi
  sleep 1
done

echo "Running migrations..."
python manage.py migrate --noinput
python manage.py showmigrations organizations bookings | tail -5
echo "Migrations done."

python manage.py collectstatic --noinput

if [ "$1" = "prod" ]; then
  exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --reload
