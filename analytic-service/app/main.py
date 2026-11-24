import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from .consumer import consume_events
from .database import mongodb_client, events_collection


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(consume_events(events_collection))

    try:
        yield
    finally:
        task.cancel()

        # тоже самое что try/except. Сделали чтоб лишние ошибки не трогались
        with suppress(asyncio.CancelledError):
            await task

        await mongodb_client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/events")
async def get_events(limit: int = 20):
    query = events_collection.find().sort("created_at", -1).limit(limit)
    return query.to_list(limit)
