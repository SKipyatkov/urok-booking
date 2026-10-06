# Промпт — Спринт 4 (polish перед пилотами / деплоем)

Проект: `/home/kipyatoook/urok-booking`. Прочитай `QA_REPORT.md`.

MVP и тесты (11/11) готовы. Это косметика и прод-подготовка.

## Задачи

1. **Подключить кастомные ошибки**
   - В `config/urls.py` добавить `handler404` и `handler500`
   - Создать простые views или использовать `django.views.defaults`
   - Убедиться, что при `DEBUG=False` отдаётся русский `404.html` / `500.html`

2. **Vendoring static (без CDN)**
   - Скачать Pico CSS и HTMX в `backend/static/vendor/`
   - Обновить `base.html` — `{% static %}` вместо CDN

3. **README — секция «Деплой»**
   - `DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS`
   - `docker compose` на VPS кратко

4. **Тест (опционально)**
   - `Client(raise_request_exception=False).get('/s/missing/book/')` с `DEBUG=False` → кастомный 404

## Не делать

- ЮKassa, Redis, дедуп Student, новые фичи

## Готово когда

- 11+ тестов OK
- `DEBUG=False` в `.env.example` с комментарием
- README обновлён

Начинай с handler404/500.
