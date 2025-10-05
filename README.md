# Cabbage — FastAPI бэкенд магазина + Telegram‑бот

Коротко: асинхронный бэкенд на FastAPI с PostgreSQL (SQLAlchemy 2.0, Alembic), Telegram‑бот на aiogram 3, заготовка интеграции ЮKassa. Архитектура слоями: API → services → repositories → models. Готово к запуску локально и через Docker Compose.

- API: товары, заказы, платёжные хуки; Swagger: /docs
- Бот: регистрация пользователя по /start, хранение Telegram ID, кнопка открытия Mini App
- БД: PostgreSQL (asyncpg), миграции через Alembic
- Платежи: заглушка ЮKassa (create + webhook)
- Логирование: централизованное, dev (консоль DEBUG) / prod (файл WARNING+)

## Что нового
- ✅ Безопасная авторизация Mini App через валидацию initData и выдачу JWT (`POST /tg/webapp/auth`).
- ✅ Переход API на Bearer JWT (с dev‑fallback по `X-Telegram-Id`).
- ✅ Режимы бота: dev — polling; prod/Docker — webhook с проверкой секрета.
- ✅ **Централизованное логирование**: dev (DEBUG в консоль), prod (WARNING+ в файл с ротацией).

## Структура
- app/
  - main.py — точка входа FastAPI (поднимает aiogram в polling/webhook)
  - api/routers — health, products, orders, payments, addresses, tg_auth
  - api/deps.py — зависимости (JWT авторизация, dev‑fallback)
  - core/ — конфиг (Pydantic Settings), БД (Async engine), логирование, middleware
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

```bash
cp .env.example .env
```

ВНИМАНИЕ: в приложении используется Pydantic Settings с env_nested_delimiter="__". Для секции YOOKASSA корректные имена переменных такого вида:
- YOOKASSA__SHOP_ID
- YOOKASSA__SECRET_KEY
- YOOKASSA__RETURN_URL
- YOOKASSA__WEBHOOK_SECRET

## Переменные окружения

### Основные
- `APP_ENV` — окружение: `dev` (по умолчанию) или `prod`
- `APP_HOST`, `APP_PORT` — хост и порт FastAPI
- `DATABASE_URL` — строка подключения к PostgreSQL

### Логирование
- `LOG_DIR` — директория для логов (по умолчанию `./logs`)
- `LOG_LEVEL` — уровень логирования (по умолчанию `INFO`)

**Поведение:**
- **Dev** (`APP_ENV=dev`): логи DEBUG/INFO выводятся в консоль, читаемый формат.
- **Prod** (`APP_ENV=prod`): логи WARNING/ERROR/CRITICAL записываются в `logs/app.log` с ротацией (10 MB × 5 файлов), минимальный вывод в консоль.

### Telegram
- `TELEGRAM_BOT_TOKEN` — токен бота
- `TELEGRAM_MODE` — `polling` (dev) или `webhook` (prod)
- `TELEGRAM_WEBHOOK_HOST` — публичный HTTPS URL (для webhook)
- `TELEGRAM_WEBHOOK_PATH` — путь webhook (по умолчанию `/telegram/webhook`)
- `TELEGRAM_WEBHOOK_SECRET` — секрет для проверки webhook

### Mini App / Frontend
- `FRONTEND_WEBAPP_URL` — URL вашего Mini App (отправляется в кнопке /start)

### JWT
- `JWT_SECRET` — секрет для подписания JWT
- `JWT_ALGORITHM` — алгоритм (по умолчанию `HS256`)
- `JWT_TTL_SECONDS` — срок жизни токена (по умолчанию 3600 сек.)
- `WEBAPP_AUTH_TTL_SECONDS` — TTL initData (по умолчанию 600 сек.)

### ЮKassa
- `YOOKASSA__SHOP_ID`, `YOOKASSA__SECRET_KEY`, `YOOKASSA__RETURN_URL`, `YOOKASSA__WEBHOOK_SECRET`

## Быстрый старт в Docker (рекомендуется)

1) **Подготовьте .env**
```bash
cp .env.example .env
# Заполните TELEGRAM_BOT_TOKEN, FRONTEND_WEBAPP_URL, JWT_SECRET
```

2) **Поднимите базу**
```bash
docker compose up -d db
```

3) **Инициализируйте миграции**
```bash
mkdir -p alembic/versions
docker compose run --rm backend uv run alembic revision --autogenerate -m "init"
docker compose run --rm backend uv run alembic upgrade head
```

4) **Запустите сервисы**
```bash
docker compose up -d backend telegram-bot
```

**Проверка:**
- API: http://localhost:8000/ (и /docs)
- Health: `GET http://localhost:8000/health/ping` → `{"status":"ok"}`

**Логи:**
```bash
docker compose logs -f backend
docker compose logs -f telegram-bot
```

## Локальная разработка (без Docker)

1) **Виртуальное окружение и зависимости**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) **База данных**
- Запустите PostgreSQL локально или поднимите только БД из compose: `docker compose up -d db`
- В .env укажите `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cabbage`

3) **Миграции**
```bash
mkdir -p alembic/versions
alembic revision --autogenerate -m "init"
alembic upgrade head
```

4) **Запуск API**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5) **Запуск бота**
```bash
python -m app.telegram.run_bot
```

## Авторизация Mini App

1) **Клиент:** в Mini App используйте `window.Telegram.WebApp.initData` (raw строка) и отправьте её на бэкенд:
```typescript
const initData = window.Telegram.WebApp.initData;
const resp = await fetch("/tg/webapp/auth", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ init_data: initData }),
});
const { token } = await resp.json();
// Сохраните token и добавляйте в Authorization: Bearer <token>
```

2) **Бэкенд:** `/tg/webapp/auth` валидирует initData как описано в доках Telegram (HMAC_SHA256("WebAppData", bot_token), TTL по auth_date), создаёт/обновляет пользователя и выдаёт JWT.

3) **Защищённые эндпоинты:** передавайте `Authorization: Bearer <jwt>`. В dev допускается `X-Telegram-Id` как fallback.

**Документация:**
- Aiogram v3: https://docs.aiogram.dev
- WebApp авторизация: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
- setWebhook: https://core.telegram.org/bots/api#setwebhook

## Режимы бота

- **Dev (polling):** `TELEGRAM_MODE=polling` — бот стартует фоном внутри FastAPI (lifespan) или отдельным модулем `app/telegram/run_bot.py`.
- **Prod (webhook):** `TELEGRAM_MODE=webhook`, обязателен публичный HTTPS. Бэкенд выставляет вебхук на `{TELEGRAM_WEBHOOK_HOST}{TELEGRAM_WEBHOOK_PATH}` и проверяет заголовок `X-Telegram-Bot-Api-Secret-Token`.

## Логирование

### Архитектура
- Централизованная настройка в `app/core/logging.py`.
- Все модули используют `logging.getLogger(__name__)`.
- Middleware `app/core/middleware.py` логирует все HTTP-запросы.

### Что логируется
- Старт/остановка приложения и бота
- HTTP-запросы (метод, путь, статус, время выполнения)
- Авторизация (успех/неудача, telegram_id)
- Создание заказов, адресов, пользователей
- Ошибки с полным traceback (`exc_info=True`)

### Примеры логов

**Dev (консоль):**
```
INFO     | app.core.logging           | Логирование настроено для окружения: dev
INFO     | app.main                   | Запуск приложения...
INFO     | api.requests               | POST /tg/webapp/auth
INFO     | app.api.routers.tg_auth    | Авторизация Mini App: telegram_id=123456
INFO     | api.requests               | POST /tg/webapp/auth - 200 - 0.123s
```

**Prod (файл `logs/app.log`):**
```
2024-01-15 10:23:45 | WARNING  | app.services.order_service | Попытка создать заказ без адреса: user_id=42
2024-01-15 10:24:12 | ERROR    | app.api.routers.tg_auth | Неожиданная ошибка при авторизации Mini App: ...
Traceback (most recent call last):
  ...
```

### Ротация логов
В prod логи автоматически ротируются:
- Максимальный размер файла: 10 MB
- Количество backup-файлов: 5
- Итого: до 50 MB логов

## Тесты
```bash
pytest
```

## Продакшен‑развёртывание

**Вариант на Docker Compose:**

1) Подготовьте .env c production‑значениями:
   - `APP_ENV=prod`
   - Реальная БД, `TELEGRAM_BOT_TOKEN`, `JWT_SECRET`
   - `TELEGRAM_MODE=webhook`, `TELEGRAM_WEBHOOK_HOST` (HTTPS)
   - `YOOKASSA__*` (если используется)

2) Соберите образы:
```bash
docker compose build
```

3) Примените миграции:
```bash
docker compose run --rm backend alembic upgrade head
```

4) Запустите сервисы:
```bash
docker compose up -d backend telegram-bot
```

5) Настройте reverse‑proxy (Nginx/Caddy) перед backend:8000, включите HTTPS.

6) В личном кабинете ЮKassa настройте webhook на `https://<ваш-домен>/payments/yookassa/callback`.

**Примечания:**
- Логи в prod пишутся в `logs/app.log` внутри контейнера. Смонтируйте volume для доступа с хоста.
- Для высокой нагрузки используйте gunicorn с воркерами uvicorn.
- Настройте мониторинг (Sentry, Grafana, ELK).

## Полезные детали реализации
- Настройки: `app/core/config.py` (Pydantic Settings), .env читается автоматически
- Alembic использует `settings.database_url` (приоритетнее alembic.ini)
- Пользователь определяется по Telegram ID (JWT или X‑Telegram‑Id в dev)
- Репозитории и сервисы изолируют бизнес‑логику от HTTP-слоя
- Логирование: `app/core/logging.py`, вызывается в начале `app/main.py` и `app/telegram/run_bot.py`
