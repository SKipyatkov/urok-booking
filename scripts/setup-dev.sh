#!/usr/bin/env bash
# Local dev setup without Docker (SQLite).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "Нужен пакет python3-venv. Ubuntu: sudo apt install python3-venv python3-pip"
  exit 1
fi

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Создан .env из .env.example"
fi

if ! grep -q '^DATABASE_URL=sqlite:' .env 2>/dev/null; then
  echo ""
  echo "Для локальной разработки без PostgreSQL добавьте в .env:"
  echo "DATABASE_URL=sqlite:///$(pwd)/backend/db.sqlite3"
  echo ""
fi

cd backend
python manage.py migrate
echo ""
echo "Готово. Запуск:"
echo "  source .venv/bin/activate"
echo "  cd backend"
echo "  python manage.py seed_demo   # опционально"
echo "  python manage.py runserver"
