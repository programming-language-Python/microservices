# если несколько клиентов то была архитектура каталога
# clients
#   catalog.py
# Это вариант сделать без брокеров, НО ЭТО БУДЕТ СИНХРОННО
import httpx


class CatalogClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get_product(self, product_id: str) -> dict:
        response = httpx.get(f"{self.base_url}/products/{product_id}")
        return response.json()


if __name__ == "__main__":
    client = CatalogClient(base_url="http://127.0.0.1:8000")
    product = client.get_product(product_id="b9e6485a-95c0-4173-bb98-d1471c74d4b7")
    print(f"Полученный объект продукта по API: {product}")
