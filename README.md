# Cabbage — FastAPI бэкенд магазина + Telegram‑бот

Коротко: асинхронный бэкенд на FastAPI с PostgreSQL (SQLAlchemy 2.0, Alembic), Telegram‑бот на aiogram 3, заготовка интеграции ЮKassa. Архитектура слоями: API → services → repositories → models. Готово к запуску локально и через Docker Compose.

- API: товары, заказы, платёжные хуки; Swagger: /docs
- Бот: регистрация пользователя по /start, хранение Telegram ID
- БД: PostgreSQL (asyncpg), миграции через Alembic
- Платежи: заглушка ЮKassa (create + webhook)

## Структура
- app/
  - main.py — точка входа FastAPI
  - api/routers — health, products, orders, payments
  - api/deps.py — зависимости (сессия БД, текущий пользователь по X‑Telegram‑Id)
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

## Быстрый старт в Docker (рекомендуется)
1) Подготовьте .env
- cp .env.example .env
- Заполните TELEGRAM_BOT_TOKEN
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
- В .env укажите DATABASE_URL, например: `postgresql+asyncpg://postgres:postgres@localhost:5432/cabbage` (если у вас локальный Postgres). Если БД из compose: `@localhost:5432` тоже подойдёт при пробросе порта.

3) Миграции
- mkdir -p alembic/versions
- uv run alembic revision --autogenerate -m "init"
- uv run alembic upgrade head

4) Запуск API
- uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

5) Запуск бота
- uv run -m app.telegram.run_bot

## Коротко об API
- GET / — {app:"cabbage", status:"ok"}
- GET /health/ping — пинг
- GET /products — список товаров с актуальной ценой
- POST /orders — создание заказа (нужен заголовок X-Telegram-Id)
- POST /payments/yookassa/callback — webhook ЮKassa (заглушка)
- POST /payments/yookassa/create — пример создания платежа (заглушка)

Документация Swagger: /docs

## Тесты
- uv run pytest

## Продакшен‑развёртывание
Вариант на Docker Compose:
- Подготовьте .env c production‑значениями (реальная БД, TELEGRAM_BOT_TOKEN, YOOKASSA__*)
- Соберите образы: `docker compose build`
- Примените миграции: `docker compose run --rm backend uv run alembic upgrade head`
- Запустите сервисы: `docker compose up -d backend telegram-bot`
- Разместите reverse‑proxy (например, Nginx) перед backend:8000, включите HTTPS
- В личном кабинете ЮKassa настройте webhook на https://<ваш-домен>/payments/yookassa/callback и задайте return_url

Примечания по производительности:
- По умолчанию используется uvicorn. Для высокой нагрузки можно использовать gunicorn с воркерами uvicorn (не входит в текущий Dockerfile).
- Настройте лимиты ресурсов контейнеров и мониторинг.

## Полезные детали реализации
- Настройки: app/core/config.py (Pydantic Settings), .env читается автоматически
- Alembic использует settings.database_url (приоритетнее alembic.ini)
- Пользователь определяется по Telegram ID (X‑Telegram‑Id в API и /start в боте)
- Репозитории и сервисы изолируют бизнес‑логику от HTTP-слоя
