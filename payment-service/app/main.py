from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request

from .config import settings
from .database import engine
from .models import Base
from .rabbitmq import declare_payment_exchange, connect_rabbitmq
from .schemas import PaymentCreateSchema, PaymentReadSchema
from .service import PaymentService
from .dependencies import get_payment_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .models import PaymentORM
    async with engine.begin() as database_connection:
        await database_connection.run_sync(Base.metadata.create_all)

    rabbitmq_connection = await connect_rabbitmq(url=settings.rabbitmq_url)
    channel = await rabbitmq_connection.channel()
    app.state.payment_exchange = await declare_payment_exchange(channel, settings.payment_exchange_name)

    try:
        yield
    finally:
        rabbitmq_connection.close()


app = FastAPI(lifespan=lifespan)


@app.get("/payments/{payment_id}", response_model=PaymentReadSchema)
async def get_payment(
        payment_id,
        payment_service: PaymentService = Depends(get_payment_service)
):
    return await payment_service.get(payment_id)


@app.get("/payments", response_model=list[PaymentReadSchema])
async def get_payment(
        payment_service: PaymentService = Depends(get_payment_service)
):
    return await payment_service.get_all()


# имитация платежа
@app.post("/payments", response_model=PaymentCreateSchema)
async def create_payment(
        request: Request,
        payload: PaymentCreateSchema,
        payment_service: PaymentService = Depends(get_payment_service)
):
    payment = await payment_service.create(payload)

    return await payment_service.complete_payment(
        payment,
        order_id=payment.order_id,
        amount=payment.amount,
        exchange=request.app.state.payment_exchange
    )
