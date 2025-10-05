# Cabbage — FastAPI бэкенд магазина + Telegram‑бот

Коротко: асинхронный бэкенд на FastAPI с PostgreSQL (SQLAlchemy 2.0, Alembic), Telegram‑бот на aiogram 3, заготовка интеграции ЮKassa. Архитектура слоями: API → services → repositories → models. Готово к запуску локально и через Docker Compose.

- API: товары, заказы, платёжные хуки; Swagger: /docs
- Бот: регистрация пользователя по /start, хранение Telegram ID, кнопка открытия Mini App
- БД: PostgreSQL (asyncpg), миграции через Alembic
- Платежи: заглушка ЮKassa (create + webhook)

## Что нового
- Безопасная авторизация Mini App через валидацию initData и выдачу JWT (`POST /tg/webapp/auth`).
- Переход API на Bearer JWT (с dev‑fallback по `X-Telegram-Id`).
- Режимы бота: dev — polling; prod/Docker — webhook с проверкой секрета.

## Структура
- app/
  - main.py — точка входа FastAPI (поднимает aiogram в polling/webhook)
  - api/routers — health, products, orders, payments, addresses, tg_auth
  - api/deps.py — зависимости (JWT авторизация, dev‑fallback)
  - core/ — конфиг (Pydantic Settings), БД (Async engine)
  - models/ — ORM‑модели: user, catalog, order
  - repositories/ — SQL‑доступ
  - services/ — бизнес‑логика (users, products, orders, payments)
  - telegram/ — бот aiogram (run_bot.py, handlers)
- alembic/ — конфигурация Alembic (env.py)
- requirements.txt, Dockerfile, docker-compose.yml, .env.example
- tests/ — пример теста health

## Требования
- Python 3.12 (для локальной разработки без Docker)
- Docker и Docker Compose (для контейнерного запуска)
- PostgreSQL (локально или через compose)

Переменные окружения берутся из .env. Скопируйте пример:

- cp .env.example .env

ВНИМАНИЕ: в приложении используется Pydantic Settings с env_nested_delimiter="__". Для секции YOOKASSA корректные имена переменных такого вида:
- YOOKASSA__SHOP_ID
- YOOKASSA__SECRET_KEY
- YOOKASSA__RETURN_URL
- YOOKASSA__WEBHOOK_SECRET

Пример из .env.example использует плоские имена (YOOKASSA_SHOP_ID и т.д.). Замените их на вариант с двойным подчёркиванием (см. выше).

## Новые переменные окружения
- FRONTEND_WEBAPP_URL — URL вашего Mini App (отправляется в кнопке /start)
- JWT_SECRET — секрет для подписания JWT
- JWT_ALGORITHM — алгоритм (HS256)
- JWT_TTL_SECONDS — срок жизни токена (сек.)
- WEBAPP_AUTH_TTL_SECONDS — TTL initData (сек.)

## Быстрый старт в Docker (рекомендуется)
1) Подготовьте .env
- cp .env.example .env
- Заполните TELEGRAM_BOT_TOKEN, FRONTEND_WEBAPP_URL, JWT_SECRET
- Убедитесь, что DATABASE_URL указывает на db из compose: `postgresql+asyncpg://postgres:postgres@db:5432/cabbage`
- Для ЮKassa при необходимости задайте YOOKASSA__*

2) Поднимите базу
- docker compose up -d db

3) Инициализируйте миграции (первичный снимок схемы)
- mkdir -p alembic/versions
- docker compose run --rm backend uv run alembic revision --autogenerate -m "init"
- docker compose run --rm backend uv run alembic upgrade head

4) Запустите сервисы
- docker compose up -d backend telegram-bot

Проверка:
- API: http://localhost:8000/ (и /docs)
- Health: GET http://localhost:8000/health/ping → {"status":"ok"}

Логи:
- docker compose logs -f backend
- docker compose logs -f telegram-bot

## Локальная разработка (без Docker)
1) Виртуальное окружение и зависимости
- python -m venv .venv
- source .venv/bin/activate
- uv pip install -r requirements.txt

2) База данных
- Запустите PostgreSQL локально или поднимите только БД из compose: `docker compose up -d db`
- В .env укажите DATABASE_URL, например: `postgresql+asyncpg://postgres:postgres@localhost:5432/cabbage`

3) Миграции
- mkdir -p alembic/versions
- uv run alembic revision --autogenerate -m "init"
- uv run alembic upgrade head

4) Запуск API
- uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

5) Запуск бота
- uv run -m app.telegram.run_bot

## Авторизация Mini App
1) Клиент: в Mini App используйте `window.Telegram.WebApp.initData` (raw строка) и отправьте её на бэкенд:
```ts
const initData = window.Telegram.WebApp.initData;
const resp = await fetch("/tg/webapp/auth", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ init_data: initData }),
});
const { token } = await resp.json();
// Сохраните token и добавляйте в Authorization: Bearer <token>
```

2) Бэкенд: `/tg/webapp/auth` валидирует initData как описано в доках Telegram (HMAC_SHA256("WebAppData", bot_token), TTL по auth_date), создаёт/обновляет пользователя и выдаёт JWT.

3) Защищённые эндпоинты: передавайте `Authorization: Bearer <jwt>`. В dev допускается `X-Telegram-Id` как fallback.

Документация:
- Aiogram v3: https://docs.aiogram.dev
- WebApp авторизация: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
- setWebhook: https://core.telegram.org/bots/api#setwebhook

## Режимы бота
- Dev (polling): `TELEGRAM_MODE=polling` — бот стартует фоном внутри FastAPI (lifespan) или отдельным модулем `app/telegram/run_bot.py`.
- Prod (webhook): `TELEGRAM_MODE=webhook`, обязателен публичный HTTPS. Бэкенд выставляет вебхук на `{TELEGRAM_WEBHOOK_HOST}{TELEGRAM_WEBHOOK_PATH}` и проверяет заголовок `X-Telegram-Bot-Api-Secret-Token`.

## Тесты
- uv run pytest
