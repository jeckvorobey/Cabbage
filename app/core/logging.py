"""Централизованная настройка логирования для dev/prod окружений."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging() -> None:
    """Настроить логирование в зависимости от окружения (dev/prod).
    
    Dev: DEBUG/INFO в консоль, читаемый формат.
    Prod: WARNING/ERROR в файл с ротацией + минимальный вывод в консоль.
    """
    # Импорт settings внутри функции, чтобы избежать циклических зависимостей
    from app.core.config import settings
    
    # Корневой логгер
    root_logger = logging.getLogger()
    
    # Уровень логирования
    if settings.app_env == "prod":
        root_logger.setLevel(logging.WARNING)
        log_level = logging.WARNING
    else:
        root_logger.setLevel(logging.DEBUG)
        log_level = logging.DEBUG
    
    # Очистка существующих хендлеров
    root_logger.handlers.clear()
    
    # Формат логов
    if settings.app_env == "prod":
        # Prod: структурированный формат с временем
        log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
    else:
        # Dev: читаемый формат
        log_format = "%(levelname)-8s | %(name)-30s | %(message)s"
        date_format = None
    
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Console handler (всегда)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (только prod)
    if settings.app_env == "prod":
        log_dir = Path(settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Настройка сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING if settings.app_env == "prod" else logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)
    
    # Логирование старта
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено для окружения: {settings.app_env}")
