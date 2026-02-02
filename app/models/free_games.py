import discord

from datetime import datetime
from typing import Optional

from tortoise import fields
from tortoise.models import Model



class FreeGame(Model):
    id: int = fields.IntField(primary_key=True) # type: ignore[assignment]

    title: str = fields.CharField(max_length=128) # type: ignore[assignment] remember to check this before assigning!
    description: str = fields.TextField() # type: ignore[assignment]
    
    url: str = fields.TextField(max_length=256) # type: ignore[assignment]
    image_url = fields.TextField(max_length=256) # type: ignore[assignment]

    start_free_date: datetime = fields.DatetimeField(auto_now=True) # type: ignore[assignment]
    end_free_date: Optional[datetime] = fields.DatetimeField(null=True) # type: ignore[assignment]