from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class NotificationCreateSchema(BaseModel):
    service: str
    type: str
    event: dict[str, Any]


class NotificationReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    service: str
    type: str
    event: dict[str, Any]
    created_at: datetime
