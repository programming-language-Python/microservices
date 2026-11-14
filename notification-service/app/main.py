from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .rabbitmq import connect_rabbitmq, start_payments_consume
from .config import settings
from .database import engine
from .models import Base
from .schemas import NotificationCreateSchema, NotificationReadSchema
from .service import NotificationService
from .dependencies import get_notification_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .models import NotificationORM

    async with engine.begin() as database_connection:
        await database_connection.run_sync(Base.metadata.create_all)

    connection = await connect_rabbitmq(url=settings.rabbitmq_url)
    await start_payments_consume(connection)

    try:
        yield
    finally:
        await connection.close()


app = FastAPI(lifespan=lifespan)


@app.get("/notifications/{notification_id}", response_model=NotificationReadSchema)
async def get_notification(
        notification_id,
        notification_service: NotificationService = Depends(get_notification_service)
):
    return await notification_service.get(notification_id)


@app.get("/notifications", response_model=list[NotificationReadSchema])
async def get_notification(
        notification_service: NotificationService = Depends(get_notification_service)
):
    return await notification_service.get_all()


@app.post("/notifications", response_model=NotificationReadSchema)
async def create_notification(
        payload: NotificationCreateSchema,
        notification_service: NotificationService = Depends(get_notification_service)
):
    return await notification_service.create(payload)
