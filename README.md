# Овощной магазин (Telegram Bot + FastAPI)

Полноценный каркас мини‑приложения интернет‑магазина овощей и фруктов.
Стек: FastAPI, PostgreSQL + SQLAlchemy (async) + Alembic, aiogram (последняя стабильная), интеграция ЮKassa, Docker. 

Документация, комментарии и код — на русском языке.

## Архитектура
- api — роуты FastAPI
- services — бизнес‑логика
- repositories — доступ к БД (async SQLAlchemy)
- models — модели SQLAlchemy
- schemas — Pydantic‑схемы (DTO)
- core — конфигурация, БД, утилиты, middleware
- telegram — модуль бота (aiogram)

## Быстрый старт (локально)
1. Создайте и заполните .env по образцу .env.example.
2. Установите зависимости: `pip install -r requirements.txt` (Python 3.12+).
3. Инициализируйте БД:
   - Создайте БД PostgreSQL.
   - Сгенерируйте миграцию: `alembic revision --autogenerate -m "init"`
   - Примените миграции: `alembic upgrade head`
4. Запустите API: `uvicorn app.main:app --reload`
5. Откройте документацию: http://localhost:8000/docs
6. Запустите Telegram‑бота: `python -m app.telegram.run_bot`

## Docker
Запуск всего стека:
- `docker compose up --build`

Сервисы:
- backend: FastAPI (http://localhost:8000)
- db: PostgreSQL
- telegram-bot: aiogram бот (polling)

## Тесты
- `pytest` — юнит‑тесты сервисов и базовые интеграционные тесты API (httpx.AsyncClient).

## Этапы разработки (из prompt.md)
1) БД: модели SQLAlchemy (async) и миграции Alembic.  
2) API: CRUD + бизнес‑правила и роли (авторизация по Telegram ID).  
3) Бот (aiogram): FSM оформления заказа, уведомления о статусах, общий сервисный слой.  
4) ЮKassa: создание платежа и обработчик callback, отражение статуса оплаты в заказах.  
5) Docker: docker-compose для backend, db, telegram-bot; примеры .env.  
6) Тесты: pytest для сервисов, API и бота.

В этом коммите реализован минимально жизнеспособный каркас (MVP): модели, базовые сервисы и эндпоинты (каталог и создание заказа), бот со /start, заготовка интеграции ЮKassa, Docker и тесты. Дальнейшее развитие предполагает расширение CRUD и ролей.
