# Промпт — Спринт 8 (Email-напоминания)

Проект: `/home/kipyatoook/urok-booking`. Спринты 6–7 готовы.

## Цель

Напоминание **родителю и преподавателю** за 24 часа до подтверждённого урока.

## Реализация (без Celery)

### 1. Модель или флаг
- Поле `Booking.reminder_sent_at` (nullable DateTime) **или** отдельная таблица `ReminderLog`
- Напоминание только для `Booking.status=confirmed`

### 2. Management command

```bash
python manage.py send_lesson_reminders
```

Логика:
- Найти бронирования: `starts_at` через 23–25 часов (окно), `status=confirmed`, напоминание ещё не отправлено
- Отправить 2 email: родителю (parent_email) и преподавателю (organization.contact_email)
- Текст на русском: имя ребёнка, дата/время в timezone org, meeting_url если есть
- Пометить `reminder_sent_at`

### 3. Cron в Docker

Добавить в `docker-compose.yml` сервис `scheduler` **или** документировать crontab на хосте:

```
0 * * * * docker compose exec -T web python manage.py send_lesson_reminders
```

(запуск раз в час достаточно)

### 4. Настройки email

- Dev: console backend (как сейчас)
- Prod: SMTP из `.env` (уже в `.env.production.example`)

### 5. Тесты

- Создать booking через 24h → command → 2 письма в outbox, флаг установлен
- Повторный запуск → не дублировать

## Не делать

- SMS, Telegram
- Напоминание за 1ч (можно TODO в коде)

## Готово когда

- command работает
- 2+ новых теста
- README: как включить cron

Начинай с миграции `reminder_sent_at` и command.
