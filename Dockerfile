# Базовый образ Python 3.12
FROM python:3.12-slim

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Рабочая директория
WORKDIR /app

# Установка uv и зависимостей проекта через uv (вместо pip)
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --install-dir /usr/local/bin

# Зависимости: сначала переносим requirements.txt для лучшего кеширования
COPY requirements.txt ./
RUN uv pip install --system --no-cache -r requirements.txt

# Копирование исходников
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY .env.example ./

# Команда запуска по умолчанию — FastAPI через uv run
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
