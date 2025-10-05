"""Middleware для логирования HTTP-запросов."""
from __future__ import annotations

import logging
import time

from fastapi import Request

logger = logging.getLogger("api.requests")


async def log_requests_middleware(request: Request, call_next):
    """Логирование всех HTTP-запросов с временем выполнения."""
    start_time = time.time()
    
    logger.info(f"{request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
        )
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"{request.method} {request.url.path} - ERROR - {duration:.3f}s: {e}",
            exc_info=True
        )
        raise
