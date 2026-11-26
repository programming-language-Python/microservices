from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer
from fastapi import Depends, FastAPI, Request

from .kafka import create_kafka_producer, publish_kafka_event
from .config import settings
from .database import engine
from .models import Base
from .rabbitmq import connect_rabbitmq, start_payments_consume
from .schemas import OrderReadSchema, OrderCreateSchema
from .service import OrderService
from .dependencies import get_order_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    from .models import Order

    Base.metadata.create_all(bind=engine)

    # RabbitMQ
    connection = await connect_rabbitmq(settings.rabbitmq_url)
    await start_payments_consume(connection)

    kafka_producer: AIOKafkaProducer = create_kafka_producer()
    await kafka_producer.start()
    app.state.kafka_producer = kafka_producer

    try:
        yield
    finally:
        await kafka_producer.stop()
        await connection.close()


app = FastAPI(lifespan=lifespan)


@app.get(
    "/orders/{order_id}",
    response_model=OrderReadSchema
)
def get_order(
        order_id: str,
        order_service: OrderService = Depends(get_order_service)
):
    return order_service.get(order_id)


@app.get(
    "/orders",
    response_model=list[OrderReadSchema]
)
def get_order(
        order_service: OrderService = Depends(get_order_service)
):
    return order_service.get_all()


@app.post(
    "/orders",
    response_model=OrderReadSchema
)
async def create_order(
        request: Request,
        payload: OrderCreateSchema,
        order_service: OrderService = Depends(get_order_service)
):
    order = order_service.create(payload)

    await publish_kafka_event(
        producer=request.app.state.kafka_producer,
        topic=settings.kafka_analytic_payment_topic,
        event=order.model_dump()
    )

    return order
