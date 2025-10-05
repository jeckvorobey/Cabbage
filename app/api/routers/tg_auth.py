"""Авторизация Telegram Mini App через валидацию initData и выдача JWT."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
import urllib.parse

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.services.user_service import UserService

router = APIRouter(prefix="/tg/webapp", tags=["tg-webapp"])
logger = logging.getLogger(__name__)


class AuthRequest(BaseModel):
    """Запрос авторизации: initData из Telegram.WebApp.initData (raw URL-encoded строка)."""

    init_data: str


class AuthResponse(BaseModel):
    token: str
    user_id: int
    telegram_id: int
    role: int


def _hmac_sha256(key: bytes, msg: bytes) -> bytes:
    """
    Вычисляет HMAC-SHA256 хэш сообщения с использованием заданного ключа.

    Args:
        key (bytes): Секретный ключ для генерации HMAC.
        msg (bytes): Сообщение, которое нужно аутентифицировать.

    Returns:
        bytes: HMAC-SHA256 хэш сообщения.
    """
    return hmac.new(key, msg, hashlib.sha256).digest()


def verify_webapp_init_data(init_data: str, bot_token: str) -> dict:
    """Проверка initData согласно https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    Шаги:
    - Разобрать URL-encoded пары в словарь.
    - Извлечь и удалить hash.
    - Построить data_check_string (ключи отсортированы, формат key=value, объединены через \n).
    - Вычислить secret = HMAC_SHA256("WebAppData", bot_token).
    - Проверить, что calc_hash == hash (hex).
    - Проверить TTL по auth_date.
    Возвращает словарь параметров initData (без hash).
    """
    try:
        pairs = urllib.parse.parse_qsl(init_data, strict_parsing=True)
    except Exception as e:
        logger.warning(f"Некорректный init_data при парсинге: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Некорректный init_data")

    data: dict[str, str] = {k: v for k, v in pairs}

    if "hash" not in data:
        logger.warning("Отсутствует hash в initData")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Отсутствует hash")
    received_hash = data.pop("hash")

    check_lines = [f"{k}={v}" for k, v in sorted(data.items())]
    data_check_string = "\n".join(check_lines).encode()

    secret = _hmac_sha256(b"WebAppData", bot_token.encode())
    calc_hash = hmac.new(secret, data_check_string, hashlib.sha256).hexdigest()

    if calc_hash != received_hash:
        logger.warning(f"Недействительный hash в initData")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный hash")

    # TTL
    try:
        auth_date = int(data.get("auth_date", "0"))
    except ValueError:
        logger.warning("Некорректный auth_date в initData")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный auth_date")

    if auth_date <= 0 or (time.time() - auth_date) > settings.webapp_auth_ttl_seconds:
        logger.warning(f"Авторизационные данные истекли: auth_date={auth_date}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Авторизационные данные истекли")

    logger.debug("initData успешно валидирован")
    return data


def issue_jwt(*, telegram_id: int, user_id: int, role: int) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "tgid": telegram_id,
        "role": role,
        "iat": now,
        "exp": now + settings.jwt_ttl_seconds,
    }
    if not settings.jwt_secret:
        logger.error("JWT_SECRET не настроен")
        raise HTTPException(status_code=500, detail="JWT не настроен")
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/auth", response_model=AuthResponse)
async def webapp_auth(req: AuthRequest, session: AsyncSession = Depends(get_session)) -> AuthResponse:
    logger.debug("Получен запрос авторизации Mini App")
    
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN не задан")
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN не задан")

    try:
        data = verify_webapp_init_data(req.init_data, settings.telegram_bot_token)

        # Поле user — JSON-строка
        try:
            user_json = json.loads(data["user"])  # type: ignore[arg-type]
        except Exception as e:
            logger.warning(f"Отсутствует или некорректен user в initData: {e}")
            raise HTTPException(status_code=400, detail="Отсутствует или некорректен user в initData")

        telegram_id = int(user_json["id"])  # гарантируется Телеграмом
        logger.info(f"Авторизация Mini App: telegram_id={telegram_id}")

        svc = UserService(session)
        user = await svc.get_or_create_by_telegram(
            telegram_id=telegram_id,
            name=user_json.get("first_name"),
            username=user_json.get("username"),
            first_name=user_json.get("first_name"),
            last_name=user_json.get("last_name"),
            is_bot=user_json.get("is_bot"),
            language_code=user_json.get("language_code"),
            is_premium=user_json.get("is_premium"),
        )

        token = issue_jwt(telegram_id=user.telegram_id, user_id=user.id, role=user.role)
        logger.info(f"JWT выдан для telegram_id={telegram_id}, user_id={user.id}")
        
        return AuthResponse(token=token, user_id=user.id, telegram_id=user.telegram_id, role=user.role)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при авторизации Mini App: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
