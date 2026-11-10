import asyncio
from uuid import uuid4

from aio_pika.abc import AbstractExchange
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PaymentORM
from .config import NotFoundError, settings
from .rabbitmq import event_publish_json
from .schemas import PaymentCreateSchema, PaymentReadSchema


class PaymentService:
    # catalog_client - нужен чтоб обращаться к другим микросервисам. Получается как архитектура клиент-серверная
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payment_data: PaymentCreateSchema) -> PaymentReadSchema:
        payment = PaymentORM(
            order_id=payment_data.order_id,
            status="created",
            amount=payment_data.amount
        )
        self.session.add(payment)
        await self.session.commit()
        return PaymentReadSchema.model_validate(payment)

    async def get(self, payment_id: str):
        payment = await self.session.get(PaymentORM, payment_id)
        if payment is None:
            raise NotFoundError

        return payment

    async def complete_payment(
            self,
            payment: PaymentORM,
            order_id: str,
            user_id: int,
            amount: int,
            exchange: AbstractExchange
    ):
        await asyncio.sleep(4)  # имитация оплаты пользователем

        payment.status = "succeeded"
        await self.session.commit()

        event = {
            "event_id": str(uuid4),
            "order_id": order_id,
            "user_id": user_id,
            "status": "succeeded",
            "amount": amount
        }

        await event_publish_json(exchange, settings.payment_succeeded_routing_key, data=event)
