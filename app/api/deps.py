"""Зависимости FastAPI: получение сессии БД и текущего пользователя.

Поддерживаются два режима авторизации:
- Основной: JWT (Authorization: Bearer), выдаётся через /tg/webapp/auth после валидации initData Mini App.
- Dev-fallback: заголовок X-Telegram-Id допускается только в окружении dev.
"""
from __future__ import annotations

import logging

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.core.db import get_session
from app.schemas.user import UserMe
from app.services.user_service import UserService
from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncSession:
    """Асинхронна�� сессия БД."""
    async for s in get_session():
        return s
    raise RuntimeError("Не удалось получить сессию БД")


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    x_telegram_id: int | None = Header(default=None, alias="X-Telegram-Id"),
    session: AsyncSession = Depends(get_db_session),
) -> UserMe:
    """Получить текущего пользователя.

    Приоритет: Bearer JWT → dev fallback X-Telegram-Id.
    """
    user_service = UserService(session)

    # 1) Bearer JWT
    if creds is not None:
        token = creds.credentials
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            user_id = int(payload.get("sub"))  # noqa: F841
            telegram_id = int(payload.get("tgid"))
            logger.debug(f"JWT авторизация: telegram_id={telegram_id}")
        except Exception as e:
            logger.warning(f"Недействительный JWT токен: {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")
        user = await user_service.get_or_create_by_telegram(telegram_id=telegram_id)
        return UserMe(id=user.id, telegram_id=user.telegram_id, role=user.role)  # type: ignore[arg-type]

    # 2) Dev fallback (устаревший путь)
    if settings.app_env == "dev" and x_telegram_id is not None:
        logger.debug(f"Dev fallback авторизация: X-Telegram-Id={x_telegram_id}")
        user = await user_service.get_or_create_by_telegram(telegram_id=x_telegram_id)
        return UserMe(id=user.id, telegram_id=user.telegram_id, role=user.role)  # type: ignore[arg-type]

    logger.warning("Попытка доступа без авторизации")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется авторизация")


def require_role_at_most(max_role: "UserRole"):
    """Проверка роли: пускает, если роль пользователя <= max_role (ADMIN=1 < MANAGER=2 < CUSTOMER=9).

    Пример: Depends(require_role_at_most(UserRole.MANAGER)) — допускает ADMIN и MANAGER,
    но отклоняет CUSTOMER.
    """
    from app.schemas.user import UserMe  # локальные импорты, чтобы избежать циклов
    from app.models.user import UserRole
    from fastapi import Depends, HTTPException, status

    async def _dep(user: UserMe = Depends(get_current_user)) -> UserMe:
        if int(user.role) > int(max_role):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
        return user

    return _dep
