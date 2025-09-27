"""Alembic env для асинхронной SQLAlchemy.

Поддерживает автогенерацию миграций, используя Base.metadata из приложения.
"""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

from alembic import context

# Конфигурация Alembic из alembic.ini
config = context.config

# Интерпретация логгинга из файла конфигурации.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импортируем метаданные моделей приложения
from app.core.db import Base  # noqa: E402
import app.models  # noqa: F401, E402  # регистрирует таблицы в метаданных

target_metadata = Base.metadata


def get_url() -> str:
    # Предпочитаем URL из переменных окружения приложения, если доступно
    try:
        from app.core.config import settings

        return settings.database_url
    except Exception:
        return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Запуск миграций в offline‑режиме.

    Использует URL соединения без подключения к БД.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в online‑режиме с async‑движком."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable: AsyncEngine = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
