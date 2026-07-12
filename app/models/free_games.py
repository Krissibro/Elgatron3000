from datetime import datetime

from tortoise import fields
from tortoise.models import Model


class FreeGame(Model):
    id: int = fields.IntField(primary_key=True)  # ty:ignore[invalid-assignment]

    title: str = fields.CharField(max_length=128)  # ty:ignore[invalid-assignment] remember to check this before assigning!
    description: str = fields.TextField()  # ty:ignore[invalid-assignment]

    url: str = fields.TextField(max_length=256)  # ty:ignore[invalid-assignment]
    image_url: str = fields.TextField(max_length=256)  # ty:ignore[invalid-assignment]

    start_free_date: datetime = fields.DatetimeField(auto_now=True)  # ty:ignore[invalid-assignment]
    end_free_date: datetime | None = fields.DatetimeField(null=True)  # ty:ignore[invalid-assignment]
