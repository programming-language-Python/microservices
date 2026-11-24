from pymongo import AsyncMongoClient

from .config import settings

mongodb_client = AsyncMongoClient(settings.mongodb_url)
# Создали БД и таблицу
events_collection = mongodb_client[settings.mongodb_database][settings.mongodb_collection]
