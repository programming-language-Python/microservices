from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .service import NotificationService


def get_notification_service(
        db: AsyncSession = Depends(get_db),
) -> NotificationService:
    return NotificationService(db)
