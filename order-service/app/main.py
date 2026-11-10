from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI

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

    try:
        yield
    finally:
        await connection.close()


app = FastAPI(lifespan=lifespan)


@app.get(
    "/orders/{order_id}",
    response_model=OrderReadSchema
)
def get_order(
        order_id: int,
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
    response_model=OrderCreateSchema
)
def create_order(
        payload: OrderCreateSchema,
        order_service: OrderService = Depends(get_order_service)
):
    return order_service.create(payload)
