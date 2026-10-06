# QA Report — Urok Booking

**Дата:** 2026-07-13, 22:05 (UTC+6) — полная проверка после спринта 10  
**Окружение:** venv + SQLite + `runserver` на `127.0.0.1:8765`  
**Вердикт:** ✅ **Готово к деплою на VPS** (после `.env`, HTTPS, ЮKassa, SMTP, cron)

---

## Автотесты

| Окружение | Результат | Примечание |
|-----------|-----------|------------|
| Локально (venv + SQLite) | **31/31 OK** | ~4.4 с |
| Docker + PostgreSQL | ⚠️ не запущен | `permission denied` на docker.sock |

```bash
cd ~/urok-booking/backend
../.venv/bin/python manage.py test tests -v2
```

### Покрытие по спринтам

| Спринт | Что тестируется |
|--------|-----------------|
| 1–4 | Бронирование, слоты, auth, rate limit, 404, static |
| 6 | `/health/` |
| 7 | Лендинг, статистика, CSV, slug |
| 8 | `send_lesson_reminders` |
| 9 | Trial, billing redirect, блок публичной записи, webhook ЮKassa |
| 10 | WebP лого, дедуп учеников, `status_badge` |

---

## Инфраструктура

| Проверка | Результат |
|----------|-----------|
| `manage.py check` | ✅ No issues |
| `makemigrations --check` | ✅ No changes |
| `seed_demo` | ✅ demo@urok-booking.local / demo12345, slug `demo-school` |
| `/health/` | ✅ `{"status": "ok"}` |
| Логотип horizontal | ✅ ~10 KB PNG + ~2 KB WebP |
| Логотип icon | ✅ ~8 KB PNG + ~2 KB WebP |
| `urok-logo-stacked.png` | ✅ удалён |
| `scripts/optimize_logos.py` | ✅ |
| `docker-compose.prod.yml` | ✅ (не прогонялся — нет Docker) |
| `.env.example` | ✅ |

---

## Ручное QA (HTTP, runserver)

| # | Сценарий | Результат |
|---|----------|-----------|
| 1 | `GET /health/` | ✅ |
| 2 | Гость на `/` — лендинг v2 (`feature-card`, `landing-preview`) | ✅ |
| 3 | `GET /login/` — WebP `<picture>`, `app.js`, `app.css` | ✅ |
| 4 | `GET /s/demo-school/book/` — шаги записи, `slot-preview` | ✅ |
| 5 | Кастомный 404 | ✅ |
| 6 | Логин → кабинет (все 7 разделов 200) | ✅ |
| 7 | Дашборд — sidebar, week-nav, stat-карточки, `data-copy` | ✅ |
| 8 | Заявки / ученики — `status-pill` или `empty-state` | ✅ |
| 9 | CSV учеников / бронирований | ✅ `text/csv` |
| 10 | `GET /cabinet/billing/` — trial, 990 ₽ | ✅ |
| 11 | Статика: `app.css`, `app.js`, `.webp` | ✅ 200 |
| 12 | `send_lesson_reminders` | ✅ `Reminders sent: 0` (нет уроков через 24 ч) |

**Замечание:** `status-pill` на календаре появляется только если в текущей неделе есть бронирования — при пустом календаре это нормально.

---

## Спринты 6–10 — статус

| Спринт | Статус |
|--------|--------|
| 6 Prod-ready | ✅ |
| 7 Stats, landing, CSV, slug | ✅ |
| 8 Напоминания | ✅ (cron на VPS — вручную) |
| 9 ЮKassa | ✅ код + тесты; боевой платёж — после ключей |
| 10 UI polish, WebP, dedup | ✅ |

---

## Перед выкладкой на VPS

- [ ] Скопировать `.env.production.example` → `.env`, заполнить `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
- [ ] Сменить пароль PostgreSQL в compose
- [ ] `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build`
- [ ] HTTPS (nginx/Caddy) → :8000
- [ ] ЮKassa: shop_id, secret, webhook `https://домен/webhooks/yookassa/`
- [ ] SMTP для писем и напоминаний
- [ ] Cron: `send_lesson_reminders` раз в час
- [ ] `DEBUG=False`, smoke-тест в браузере

---

## Мелочи (не блокер)

| Замечание | Действие |
|-----------|----------|
| Docker недоступен без `sudo`/группы `docker` | На VPS или `sudo usermod -aG docker $USER` |
| Rate limit in-memory | При 3+ workers — Redis позже |
| Напоминания вручную | Нужен confirmed booking ~через 24 ч для проверки |

---

## Демо

```bash
cd ~/urok-booking
docker compose up -d   # или runserver локально
docker compose exec web python manage.py seed_demo
```

| | |
|--|--|
| Лендинг | http://localhost:8000/ |
| Вход | http://localhost:8000/login/ (`demo@urok-booking.local` / `demo12345`) |
| Запись | http://localhost:8000/s/demo-school/book/ |
| Оплата | http://localhost:8000/cabinet/billing/ |

---

## Итог

**31 автотест, ручные сценарии и спринт 10 — в порядке.** Код готов к деплою. Следующий шаг — VPS + домен + ЮKassa + первые пилоты.
