import json

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractExchange, AbstractIncomingMessage, \
    AbstractConnection

from .config import settings
from .database import SessionLocal
from .schemas import NotificationCreateSchema
from .service import NotificationService


async def connect_rabbitmq(url: str) -> AbstractRobustConnection:
    return await aio_pika.connect_robust(url)


# в идеале аннатировать, что содержит message
async def handler_events(message: AbstractIncomingMessage):
    async with message.process():
        event = json.loads(message.body.decode('utf-8'))
        notification_data = NotificationCreateSchema(
            service="payment-service",
            type=settings.payment_succeeded_routing_key,
            event=event
        )

        # Depends здесь не работает, т.к. эту функцию вызывает aio_pika, а не FastAPI
        async with SessionLocal() as session:
            notification_service = NotificationService(session)
            await notification_service.create(notification_data)
            # здесь добавляется логирование


async def start_payments_consume(connection: AbstractConnection):
    # логика написания channel другая по сравнению с payment-service
    channel = await connection.channel()
    payment_exchange = await channel.declare_exchange(settings.payment_exchange_name)
    notification_queue = await channel.declare_queue(settings.notification_queue_name)

    await notification_queue.bind(payment_exchange, routing_key=settings.payment_succeeded_routing_key)
    await notification_queue.consume(handler_events)  # происходит бесконечно - ожидает сообщение
