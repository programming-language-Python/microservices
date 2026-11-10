# если несколько клиентов то была архитектура каталога
# clients
#   catalog.py
# Это вариант сделать без брокеров, НО ЭТО БУДЕТ СИНХРОННО
import httpx


class PaymentClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def create_payment(self, order_id: str, amount: int) -> dict:
        # это нужно через Pydantic делать для простоты это опущено
        json_data = {"order_id": order_id, "amount": amount}
        response = httpx.post(f"{self.base_url}/payments", json=json_data)
        response.raise_for_status()
        return response.json()
