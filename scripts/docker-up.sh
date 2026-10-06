#!/bin/sh
# Поднять Docker, применить миграции, загрузить демо-данные
set -e
cd "$(dirname "$0")/.."

docker compose up -d --build

echo "Ожидание готовности web..."
for i in $(seq 1 30); do
  if docker compose exec -T web python manage.py migrate --check >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

docker compose exec -T web python manage.py migrate --noinput
docker compose exec -T web python manage.py seed_demo

echo ""
echo "Готово: http://localhost:8000"
echo "Демо: demo@urok-booking.local / demo12345"
