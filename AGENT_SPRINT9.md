# Промпт — Спринт 9 (ЮKassa — подписка)

Проект: `/home/kipyatoook/urok-booking`. Спринты 6–8 готовы.

**Важно:** для реальных платежей нужны **самозанятость или ИП** и магазин в [ЮKassa](https://yookassa.ru/). В dev используй **тестовый shop_id и secret_key**.

## Цель

Преподаватель может **оплатить подписку** и разблокировать полный доступ (или trial 14 дней при регистрации).

## Тарифы (из README)

| План | Цена | Лимит |
|------|------|-------|
| trial | 0 | 14 дней с регистрации |
| solo | 990 ₽/мес | 1 преподаватель |
| school | 2490 ₽/мес | до 5 преподавателей (v1 — только solo) |

## Модель

Расширить `Organization`:
- `plan`: trial | solo | school
- `trial_ends_at`, `subscription_paid_until` (DateTime)
- `yookassa_payment_id` (последний платёж, optional)

Middleware или mixin: если trial истёк и нет подписки — кабинет показывает **страницу оплаты**, публичная запись **работает** (чтобы не терять лидов) или **блокируется** — выбери **блокировку публичной записи** с баннером «школа не принимает заявки» (проще для v1).

## Поток оплаты

1. `/cabinet/billing/` — текущий план, кнопка «Оплатить 990 ₽/мес»
2. Создать платёж через ЮKassa API (redirect confirmation)
3. Webhook `/webhooks/yookassa/` — подтверждение → продлить `subscription_paid_until` на 30 дней
4. Страница успеха `/cabinet/billing/success/`

Используй официальный SDK `yookassa` (PyPI) или аккуратные HTTP-запросы.

## Env

```env
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
YOOKASSA_RETURN_URL=https://your-domain.ru/cabinet/billing/success/
```

## Безопасность

- Webhook: проверять IP ЮKassa или подпись (по документации)
- Не хранить secret в коде
- В тестах — mock API

## Тесты

- trial активен → доступ к кабинету OK
- trial истёк → редирект на billing
- webhook payment.succeeded → subscription_paid_until обновлён

## Не делать

- Автопродление без webhook (только по webhook)
- Несколько тарифов school в v1 — только solo 990₽

## Готово когда

- Тестовый платёж в sandbox проходит
- 3+ новых теста с mock
- README: настройка ЮKassa

Начинай с модели Organization + страница billing (без API), затем интеграция.
