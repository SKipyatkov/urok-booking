# Промпт для агента-разработчика

Скопируй содержимое блока ниже в новый чат Cursor Agent.

---

Ты — senior Python-разработчик. Твоя задача: реализовать MVP веб-сервиса «Urok Booking» по спецификации в README.md этого репозитория.

## Контекст продукта

SaaS для репетиторов и маленьких онлайн-школ в России.
Главная ценность: публичная ссылка для записи на пробный урок + календарь и статусы учеников в личном кабинете.
НЕ делаем: свой видеочат (Zoom), онлайн-оплату, мобильное приложение, домашки.

## Технические требования

- Python 3.12+, Django 5
- PostgreSQL в проде, SQLite допустим только локально на первом шаге
- Frontend: Django templates + HTMX + минимальный CSS (можно Pico CSS или Tailwind via CDN — без тяжёлого JS-фреймворка)
- Аутентификация: встроенная Django auth (email как username)
- Время: хранить в UTC, отображать в timezone организации (Europe/Moscow по умолчанию)
- Язык интерфейса: русский
- Код: type hints, docstrings на публичных функциях, без over-engineering

## MVP scope (строго)

1. Регистрация преподавателя → создаётся Organization + Teacher
2. Настройка расписания (дни недели, рабочие часы)
3. Публичная страница /s/{slug}/book — выбор слота и форма заявки
4. Личный кабинет: календарь бронирований, список учеников, статусы
5. Email-уведомления при новой записи (console backend для dev)
6. Поле meeting_url на бронировании (ручная вставка ссылки на Телемост)

## Модели (минимум)

- Organization (slug уникальный, name, description, timezone, slot_duration_minutes)
- Teacher (FK organization, user FK)
- Student (parent_name, parent_email, parent_phone, child_name, child_age, status)
- AvailabilityRule (teacher, weekday, start_time, end_time)
- Booking (teacher, student, starts_at, ends_at, type, status, meeting_url)

## Бизнес-правила

- Слоты генерируются из AvailabilityRule минус существующие Booking и BlockedSlot
- Длительность слота: из organization.slot_duration_minutes (30 или 60)
- При публичной записи: Student создаётся со status=new, Booking со status=pending
- Преподаватель может перевести в confirmed и сменить статус ученика на trial/active
- Два одновременных бронирования на один слот невозможны (DB constraint + проверка в сервисе)

## Порядок работы

1. Прочитай README.md полностью
2. Создай структуру проекта и docker-compose.yml
3. Реализуй модели и миграции
4. Реализуй auth и кабинет преподавателя
5. Реализуй публичную страницу записи
6. Добавь email-уведомления
7. Напиши тесты на критичные сценарии (бронирование, коллизия слотов)
8. Обнови README секцией «Как запустить локально»

## Качество

- `python manage.py test` проходит
- `docker compose up` поднимает проект с нуля
- Нет секретов в коде — только .env
- Минимальный diff, без лишних абстракций

## Не делать без явной просьбы

- React/Vue SPA
- Celery/Redis (пока не нужны)
- API-only без server-rendered страниц
- Интеграция с ЮKassa, Jitsi, Telegram-ботами
- Мультитенантность сложнее одной Organization на пользователя в v1

## Первый спринт (сделай сейчас)

Спринт 1: scaffold + модели + миграции + admin Django + регистрация/логин + пустой dashboard.
Остановись и кратко отчитайся: что сделано, как запустить, что в спринте 2.

Начинай с чтения README.md и создания файловой структуры.
