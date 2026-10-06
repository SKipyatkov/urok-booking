# Sprint 10 — UI polish, logo WebP, student dedup

## Цели

1. **Лого** — WebP (~1 KB), скрипт `scripts/optimize_logos.py`, удалён `urok-logo-stacked.png`
2. **UI/UX** — боковая навигация кабинета, статус-пилюли, тост при копировании ссылки, шаги записи, лендинг с превью, навигация по неделям в календаре
3. **Фичи** — дедупликация учеников по email + имя ребёнка; повторная заявка после «Отказ» → статус «Новый»

## Файлы

- `backend/static/js/app.js` — copy toast, выбор слота
- `backend/static/css/app.css` — sidebar, pills, landing v2
- `backend/templates/cabinet/base.html` — layout
- `backend/bookings/services/booking.py` — `_get_or_create_student`
- `backend/bookings/templatetags/booking_extras.py` — `status_badge`, `nav_active`
- `tests/test_sprint10.py`

## Проверка

```bash
python3 scripts/optimize_logos.py
docker compose exec web python manage.py test tests -v2
```
