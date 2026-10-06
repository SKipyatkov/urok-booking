#!/usr/bin/env bash
# Установка pip и Docker на Ubuntu (нужен sudo)
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Запусти с sudo:"
  echo "  sudo bash /home/kipyatoook/urok-booking/scripts/setup-system.sh"
  exit 1
fi

REAL_USER="${SUDO_USER:-$USER}"
export DEBIAN_FRONTEND=noninteractive

wait_for_apt() {
  local max_wait=600
  local waited=0

  while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 \
     || fuser /var/lib/dpkg/lock >/dev/null 2>&1 \
     || fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
    if (( waited == 0 )); then
      echo "==> Жду освобождения apt (часто это unattended-upgrades)..."
      ps aux | grep -E 'unattended-upgr|apt|dpkg' | grep -v grep || true
    fi
    if (( waited >= max_wait )); then
      echo "Ошибка: apt заблокирован дольше ${max_wait} сек."
      echo "Проверь: ps aux | grep unattended-upgr"
      echo "Обычно достаточно подождать 5–15 минут и запустить скрипт снова."
      exit 1
    fi
    sleep 5
    waited=$((waited + 5))
    echo "   ... ещё ${waited} сек"
  done
}

echo "==> Ожидание блокировки apt..."
wait_for_apt

echo "==> Обновление списка пакетов..."
apt-get update

echo "==> Установка pip, venv, curl..."
apt-get install -y python3-pip python3-venv curl ca-certificates

echo "==> Установка Docker и Docker Compose..."
apt-get install -y docker.io docker-compose-v2

echo "==> Добавление пользователя $REAL_USER в группу docker..."
usermod -aG docker "$REAL_USER"

echo "==> Запуск Docker..."
systemctl enable --now docker

echo ""
echo "Готово. Проверка:"
python3 --version
python3 -m pip --version
docker --version
docker compose version

echo ""
echo "ВАЖНО: чтобы docker работал без sudo, перелогинься"
echo "(выйди из сессии и зайди снова) или выполни: newgrp docker"
echo ""
echo "Проверка после перелогина:"
echo "  docker run --rm hello-world"
