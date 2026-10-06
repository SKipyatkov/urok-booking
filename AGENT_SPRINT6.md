# Промпт — Спринт 6 (Prod-ready)

Проект: `/home/kipyatoook/urok-booking`. Прочитай `DEPLOY_ROADMAP.md` и `QA_REPORT.md`.

## Цель

Подготовить проект к VPS **без новых пользовательских фич**.

## Задачи

### 1. Оптимизация логотипов
- Сжать `backend/static/img/urok-logo-horizontal.png` и `urok-logo-icon.png` до **&lt;100 KB** каждый (Pillow или `pngquant` если доступен)
- Сохранить визуальное качество для шапки и favicon
- Обновить `width`/`height` в шаблонах при необходимости

### 2. Healthcheck
- `GET /health/` → JSON `{"status": "ok"}` (200), без auth
- Добавить в `docker-compose.yml` healthcheck для `web`

### 3. Production Docker
- Создать `docker-compose.prod.yml` (или `docker-compose.override.prod.yml`):
  - gunicorn **без** `--reload`, 2–3 workers
  - `DEBUG=False` из `.env`
- Документировать в README: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

### 4. Security settings (`config/settings.py`)
При `DEBUG=False` включить (если ещё нет):
- `SECURE_PROXY_SSL_HEADER`
- `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- `SECURE_BROWSER_XSS_FILTER`, `SECURE_CONTENT_TYPE_NOSNIFF`
- Читать `CSRF_TRUSTED_ORIGINS` из env (через запятую)

### 5. Env
- Создать `.env.production.example` с комментариями для VPS
- Не коммитить реальные секреты

### 6. Тесты
- Тест: `/health/` возвращает 200
- Все 14+ существующих тестов должны проходить

## Не делать

- Новые фичи, ЮKassa, напоминания, лендинг

## Готово когда

- Логотипы &lt;100 KB
- `docker compose exec web python manage.py test tests -v2` — OK
- README обновлён (секция Prod)

Начинай с сжатия логотипов и `/health/`.
