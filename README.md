# Urok Booking

Веб-сервис записи на пробные и регулярные уроки для репетиторов и маленьких онлайн-школ (в т.ч. школ программирования для детей).

**Рынок:** Россия  
**Модель:** подписка (B2B — репетиторы и мини-школы)  
**Статус:** идея → MVP в разработке

---

## Суть продукта

Родитель переходит по ссылке школы → выбирает слот → оставляет контакты → получает подтверждение.  
Преподаватель видит календарь, заявки и статусы учеников в личном кабинете.

**Не делаем в v1:** свой Zoom, онлайн-оплату, домашки, мобильное приложение.

**Видео в v1:** поле «ссылка на занятие» (Яндекс.Телемост / VK) + кнопка «Открыть».  
**Видео в v2:** встроенная комната на Jitsi (не самописный WebRTC).

---

## Целевая аудитория

| Сегмент | Боль |
|---------|------|
| Репетитор 1-на-1 | Заявки теряются в переписке, нет единого календаря |
| Мини-школа (2–5 преподавателей) | Сложно вести пробные уроки и конверсию в оплату |
| Будущая онлайн-школа программирования (создатель проекта) | Нужен инструмент до открытия ИП |

---

## Конкурентное отличие

- Узкая ниша: **уроки и дети**, не салоны красоты
- Воронка: заявка → пробный → учится → отказ
- Простая публичная ссылка для соцсетей и Avito
- Дешевле и проще YClients для соло-репетитора

---

## Тарифы (черновик)

| Тариф | Цена | Лимиты |
|-------|------|--------|
| Соло | 790–990 ₽/мес | 1 преподаватель, до 30 учеников |
| Школа | 1990–2990 ₽/мес | до 5 преподавателей |
| Пробный | 14 дней бесплатно | полный функционал MVP |

Платежи — после оформления самозанятости/ИП (ЮKassa). До этого: бесплатные пилоты.

---

## Подробный план разработки

### Фаза 0 — Валидация (1 неделя, можно параллельно с кодом)

- [ ] 5 интервью с репетиторами / мини-школами
- [ ] Вопросы: как записывают на пробный, где теряют лиды, чем пользуются
- [ ] Лендинг с кнопкой «Ранний доступ» (можно на том же домене позже)
- [ ] 10 холодных сообщений: ищем 3–5 бесплатных пилотов

**Критерий успеха:** 3 человека готовы попробовать MVP.

---

### Фаза 1 — MVP backend + admin (недели 1–2)

**Стек (рекомендуемый):**
- Python 3.12+
- Django 5 + Django REST Framework (или FastAPI — на усмотрение агента, предпочтение Django за скорость admin)
- PostgreSQL (SQLite только для локальной разработки)
- Шаблоны: Django templates + HTMX (без отдельного React на старте)
- Email: console backend локально, SMTP (или Resend) в проде

**Модели данных:**

```
Organization (школа/репетитор)
  - name, slug, description, contact_email, timezone
  - plan (free_trial / solo / school)

Teacher
  - organization FK, name, email, is_active

Student (лид/ученик)
  - organization FK, parent_name, parent_email, parent_phone
  - child_name, child_age, notes
  - status: new | trial | active | rejected

AvailabilitySlot (шаблон доступности)
  - teacher FK, weekday (0-6), start_time, end_time

Booking
  - organization FK, teacher FK, student FK
  - starts_at, ends_at (datetime)
  - type: trial | regular
  - status: pending | confirmed | cancelled | completed
  - meeting_url (nullable) — ссылка на Телемост

BlockedSlot (исключения из расписания)
  - teacher FK, starts_at, ends_at, reason
```

**Функции admin/кабинета преподавателя:**
- Регистрация / вход (email + пароль)
- CRUD организации и профиля
- Настройка расписания (дни недели + часы)
- Календарь занятий (неделя)
- Список учеников с фильтром по статусу
- Смена статуса ученика и бронирования
- Поле meeting_url на бронировании
- Копируемая публичная ссылка: `/s/{slug}/book`

---

### Фаза 2 — Публичная страница записи (неделя 2–3)

**URL:** `/s/{slug}/book`

**Поток:**
1. Родитель видит название школы и описание
2. Выбирает дату → видит свободные слоты (30 или 60 мин — настройка org)
3. Заполняет: имя родителя, email, телефон, имя ребёнка, возраст, комментарий
4. Подтверждение → создаётся Student (status=new) + Booking (status=pending)
5. Email родителю: «Вы записаны на …»
6. Email преподавателю: «Новая заявка от …»

**Валидация:**
- Нельзя забронировать занятый слот
- Нельзя бронировать в прошлое
- Rate limit на публичную форму (защита от спама)

---

### Фаза 3 — Полировка и деплой (неделя 3–4)

- [ ] Адаптивная вёрстка (мобильный приоритет — родители с телефона)
- [ ] Страница 404/500
- [ ] Docker Compose (web + postgres)
- [ ] Деплой: VPS (Timeweb / Selectel / любой), nginx, Let's Encrypt
- [ ] Бэкапы БД
- [ ] Базовые тесты: бронирование слота, коллизии, публичная форма

**Критерий готовности MVP:** пилот может дать ссылку родителю, родитель записывается, преподаватель видит запись в кабинете.

---

### Фаза 4 — После MVP (не начинать до 5 пилотов)

- Онлайн-оплата (ЮKassa)
- Напоминания за 24ч и за 1ч (email)
- Несколько преподавателей в одной организации
- Встроенная комната Jitsi на `/lesson/{booking_id}`
- Экспорт учеников в CSV
- Аналитика: конверсия пробный → оплата

---

## Структура репозитория (целевая)

```
urok-booking/
├── README.md
├── AGENT.md              # промпт для агента (дублирует секцию ниже)
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── manage.py
│   ├── config/           # settings, urls, wsgi
│   ├── accounts/         # User, auth
│   ├── organizations/    # Organization, Teacher
│   ├── bookings/         # Student, Booking, Availability
│   └── templates/
├── static/
└── tests/
```

---

## Переменные окружения (.env.example)

```env
DEBUG=True
SECRET_KEY=change-me
DATABASE_URL=postgres://user:pass@localhost:5432/urok_booking
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@example.com
```

---

## Метрики успеха

| Этап | Метрика |
|------|---------|
| MVP | 3–5 пилотов используют 2+ недели |
| Месяц 2 | 10+ организаций зарегистрировано |
| Месяц 6 | 10+ платящих или 25k ₽ MRR |
| Год | Создатель открывает свою школу на этом же продукте |

---

## Промпт для агента-разработчика

Скопируй блок ниже в новый чат с агентом или используй файл `AGENT.md`.

---

```
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
```

---

## Как запустить локально

### Требования

- Python 3.12+
- Docker и Docker Compose (для PostgreSQL) **или** SQLite для быстрого старта

### Вариант 1: Docker Compose (рекомендуется)

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec web python manage.py migrate   # после обновления кода
docker compose exec web python manage.py seed_demo
```

Или одной командой: `./scripts/docker-up.sh`

Приложение: http://localhost:8000

### Вариант 2: Без Docker (SQLite)

```bash
./scripts/setup-dev.sh
source .venv/bin/activate
```

В `.env` для SQLite (скрипт подскажет, если не задано):

```env
DATABASE_URL=sqlite:////absolute/path/to/urok-booking/backend/db.sqlite3
```

```bash
cd backend
python3 manage.py seed_demo
python3 manage.py runserver
```

### Тесты

```bash
cd backend
python3 manage.py test tests -v2
```

Или через Docker (если локально нет `python`/`venv`):

```bash
docker compose exec web python manage.py test tests -v2
```

### Основные URL

| URL | Описание |
|-----|----------|
| `/register/` | Регистрация преподавателя |
| `/login/` | Вход |
| `/` | Лендинг (гости) / редирект в кабинет (авторизованные) |
| `/health/` | Healthcheck JSON `{"status": "ok"}` |
| `/cabinet/` | Личный кабинет |
| `/cabinet/billing/` | Подписка и оплата |
| `/cabinet/blocked/` | Блокировки времени |
| `/cabinet/students/export/` | CSV учеников |
| `/cabinet/bookings/export/` | CSV бронирований |
| `/s/{slug}/book/` | Публичная запись (например `/s/demo-school/book/`) |
| `/admin/` | Django admin |

### Переменные окружения

См. `.env.example`. Секреты не хранятся в коде — только в `.env`.

---

## Деплой на VPS (кратко)

### 1. Подготовка сервера

- Ubuntu 22.04+ / 24.04+
- Установите Docker и Docker Compose
- Домен указывает на IP сервера (A-запись)

### 2. Клонирование и настройка

```bash
git clone <your-repo> urok-booking
cd urok-booking
cp .env.example .env
```

В `.env` для продакшена:

```env
DEBUG=False
SECRET_KEY=<случайная строка 50+ символов>
ALLOWED_HOSTS=your-domain.ru,www.your-domain.ru
DATABASE_URL=postgres://urok:<strong-password>@db:5432/urok_booking
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# + настройки SMTP
```

Смените пароль PostgreSQL в `docker-compose.yml` (`POSTGRES_PASSWORD`) и в `DATABASE_URL`.

### 3. Запуск

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_demo  # опционально
```

**Продакшен** (gunicorn без `--reload`, 3 workers, healthcheck):

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Скопируйте `.env.production.example` → `.env` и заполните секреты.

### 4. HTTPS (рекомендуется)

Поставьте **nginx** или **Caddy** перед контейнером как reverse proxy на порт `8000`, выпустите сертификат Let's Encrypt.

Пример фрагмента nginx:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.ru;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Бэкапы

Регулярно бэкапьте volume PostgreSQL:

```bash
docker compose exec db pg_dump -U urok urok_booking > backup.sql
```

### Статика

CSS и JS (Pico, HTMX) лежат в `backend/static/` и собираются через `collectstatic` при старте контейнера. CDN не требуется.

### Напоминания за 24 часа

Команда отправляет email родителю и школе для подтверждённых уроков через ~24 часа:

```bash
docker compose exec web python manage.py send_lesson_reminders
```

На VPS — cron раз в час:

```cron
0 * * * * cd /path/to/urok-booking && docker compose exec -T web python manage.py send_lesson_reminders
```

### ЮKassa (подписка)

В `.env` укажите `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, `YOOKASSA_RETURN_URL`.  
Webhook: `https://your-domain.ru/webhooks/yookassa/` — должен быть доступен из интернета.

При регистрации — 14 дней пробного периода. После истечения кабинет ведёт на `/cabinet/billing/`, публичная запись блокируется.

---

## Лицензия

Приватный проект. Все права у создателя.
