import json

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractExchange, AbstractConnection, AbstractIncomingMessage

from .config import settings
from .database import SessionLocal
from .models import Order


# Consumer

async def connect_rabbitmq(url: str) -> AbstractRobustConnection:
    return await aio_pika.connect_robust(url)


# в идеале аннатировать, что содержит message
async def handler_payment_events(message: AbstractIncomingMessage):
    async with message.process():
        event = json.loads(message.body.decode('utf-8'))
        # Depends здесь не работает, т.к. эту функцию вызывает aio_pika, а не FastAPI
        with SessionLocal() as session:
            order = session.get(Order, event["order_id"])
            order.status = "paid"
            session.commit()
            # здесь добавляется логирование


async def start_payments_consume(connection: AbstractConnection):
    # логика написания channel другая по сравнению с payment-service
    channel = await connection.channel()
    payment_exchange = await channel.declare_exchange(settings.payment_exchange_name)
    payment_queue = await channel.declare_queue(settings.payment_queue_name)

    await payment_queue.bind(payment_exchange, routing_key=settings.payment_succeeded_routing_key)
    await payment_queue.consume(handler_payment_events)  # происходит бесконечно - ожидает сообщение


async def event_publish_json(exchange: AbstractExchange, routing_key: str, data: dict) -> None:
    message = aio_pika.Message(json.dumps(data).encode())
    await exchange.publish(message, routing_key)
