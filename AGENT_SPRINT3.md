# Промпт — Спринт 3 (мелкие фиксы после QA)

Проект: `/home/kipyatoook/urok-booking`. Прочитай `QA_REPORT.md`.

## Задачи (быстро, один PR)

1. **Миграция accounts**
   - Запусти `python manage.py makemigrations accounts` в Docker
   - Убедись, что после `migrate` нет warning «accounts have changes...»
   - Если `0002` дублирует `0003` — оставь одну корректную цепочку миграций

2. **Удалить дубликат**
   - В `backend/bookings/views_cabinet.py` класс `BlockedSlotsView` объявлен дважды (строки ~243 и ~287)
   - Оставь одну реализацию

3. **Тест (опционально)**
   - Тест: BlockedSlot исключает слот из `get_available_slots`

## Не делать

- Новые фичи, ЮKassa, Redis, React

## Готово когда

- `docker compose up` без warning про accounts
- `python manage.py test tests -v2` — 10+ тестов OK
- Краткий отчёт в чате

Начинай с `makemigrations accounts`.
