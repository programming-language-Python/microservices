from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import NotificationORM
from .config import NotFoundError
from .schemas import NotificationCreateSchema


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification_data: NotificationCreateSchema):
        notification = NotificationORM(**notification_data.model_dump())
        self.session.add(notification)
        await self.session.commit()
        return notification

    async def get_all(self):
        stmt = select(NotificationORM)
        return list((await self.session.scalars(stmt)).all())

    async def get(self, notification_id: str):
        notification = await self.session.get(NotificationORM, notification_id)
        if notification is None:
            raise NotFoundError

        return notification
