# Промпт — Спринт 2 (после QA)

Скопируй в новый чат Agent в папке `~/urok-booking`.

---

Ты — senior Python/Django разработчик. Проект Urok Booking — MVP уже работает. Прочитай `QA_REPORT.md` и `README.md` перед началом.

## Контекст QA

- 7/7 автотестов проходят в Docker
- Ручной поток записи и кабинета работает
- Есть незакоммиченная миграция accounts, баг timezone в DatePickerForm, сломанный локальный venv в README

## Задачи спринта 2 (по приоритету)

### 1. Исправить баги из QA

- [ ] Создать и применить миграцию `accounts/migrations/0002_alter_user_managers.py`
- [ ] Исправить `DatePickerForm.clean_date`: сравнивать с «сегодня» в timezone организации (для публичной страницы передавать org или timezone)
- [ ] Rate limit: увеличивать счётчик только после успешного `create_public_booking`, не на каждый POST
- [ ] Добавить `scripts/setup-dev.sh`: venv + pip install + migrate + подсказка про SQLite

### 2. Тесты

- [ ] Тест: DatePickerForm отклоняет «вчера» по Moscow даже если UTC уже следующий день (mock timezone)
- [ ] Тест: cabinet booking detail POST меняет status и meeting_url
- [ ] Тест: rate limit не срабатывает на невалидную форму (пустой slot_start)

### 3. UX улучшения (малый scope)

- [ ] UI в кабинете для BlockedSlot: страница `/cabinet/blocked/` — добавить/удалить блокировку на дату+время
- [ ] На странице ученика показывать список его бронирований
- [ ] Кастомные шаблоны `404.html`, `500.html` (минимальные, на русском)

### 4. Статика без CDN (опционально, если быстро)

- [ ] Скачать Pico CSS и HTMX в `backend/static/vendor/`, обновить `base.html`

## Не делать в этом спринте

- ЮKassa, Jitsi, Telegram, Celery/Redis
- React SPA, мультитенантность, несколько преподавателей
- Дедупликация Student (только если останется время — отдельным коммитом)

## Критерии готовности

- `docker compose exec web python manage.py test tests -v2` — все тесты зелёные
- При старте `docker compose up` нет warning про unmigrated accounts
- `QA_REPORT.md` обновлён: закрытые пункты отмечены
- Краткий отчёт в чате: что сделано, как проверить

## Порядок работы

1. Прочитай QA_REPORT.md
2. Исправь миграцию и timezone баг
3. Добавь тесты
4. BlockedSlot UI + 404/500
5. Обнови README и QA_REPORT.md

Начинай с миграции accounts и timezone fix.
