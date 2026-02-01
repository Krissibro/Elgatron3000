import discord

from datetime import datetime
from typing import Optional
from tortoise import fields
from tortoise.models import Model

from app.utilities.validators import validate_messageable

class Pin(Model):
    id: int = fields.IntField(primary_key=True)             # type: ignore[assignment]

    server_id: int = fields.IntField()                      # type: ignore[assignment]
    channel_id: int = fields.IntField()                     # type: ignore[assignment]
    message_id: int = fields.IntField()                     # type: ignore[assignment]

    message_content: str = fields.TextField()               # type: ignore[assignment]
    created_at: datetime = fields.DatetimeField()           # type: ignore[assignment]

    user_name: str = fields.CharField(max_length=32)        # type: ignore[assignment]
    user_icon: str = fields.CharField(max_length=128)       # type: ignore[assignment]
    has_files: bool = fields.BooleanField(default=False)    # type: ignore[assignment]

    def get_message_link(self) -> str:
        return f"https://discord.com/channels/{self.server_id}/{self.channel_id}/{self.message_id}"
    
    def get_icon_link(self) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.user_name}/{self.user_icon}"
    
    async def _fetch_message(self, bot) -> Optional[discord.Message]:
        guild: Optional[discord.Guild] = bot.get_guild(self.server_id)
        if guild is None:
            return
        channel = guild.get_channel(self.channel_id)
        channel = validate_messageable(channel)
        try:
            message = await channel.fetch_message(self.message_id)
        except Exception:
            message = None
        return message