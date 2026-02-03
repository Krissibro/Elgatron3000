import discord

from typing import AsyncIterable, Optional
from tortoise.expressions import RawSQL
from tortoise import BaseDBAsyncClient

from app.core.elgatron import Elgatron
from app.utilities.errors import ElgatronError
from app.models.pin_model import Pin
from app.utilities.decorators import transaction

class PinDB:
    @transaction
    async def load_random_pin(self, connection: Optional[BaseDBAsyncClient] = None) -> Pin:
        """Loads a random pin from the stored chunks."""
        pin = (
            await Pin.annotate(order=RawSQL("RANDOM()"))
            .using_db(connection)
            .order_by("order")
            .first()
        )
        if pin is None:
            raise ElgatronError("No pinned messages found.")
        return pin

    @transaction
    async def add_pin(self, message: discord.Message, connection: Optional[BaseDBAsyncClient] = None) -> None:
        """Adds a pin to the storage."""
        author = message.author
        guild = message.guild
        channel = message.channel
        if guild is None:
            raise ElgatronError("Can only add pins in a server")
        
        await Pin.create(
            server_id=guild.id,
            channel_id=channel.id,
            message_id=message.id,
            message_content=message.content,
            created_at=message.created_at,
            user_name=author.name,
            user_icon=author.avatar.url if author.avatar is not None else "",
            has_files=bool(message.attachments),
            using_db=connection
        )

    @transaction
    async def remove_pin(self, message: discord.Message, connection: Optional[BaseDBAsyncClient] = None) -> None:
        """Removes a pin from the storage."""
        guild = message.guild
        channel = message.channel
        if guild is None:
            raise ElgatronError("Can only remove pins in a server")
        
        await Pin.filter(server_id=guild.id, channel_id=channel.id, message_id=message.id).using_db(connection).delete()

    @transaction
    async def fetch_pins(self, bot: Elgatron, connection: Optional[BaseDBAsyncClient] = None) -> None:
        self.pins = []
        guild = bot.get_guild(bot.guild_id)
        if guild is None:
            print("Guild not found!")
            return

        # Fetch pins from all channels
        for i, channel in enumerate(guild.text_channels):
            # loading bar
            print(f"|{(i * '#'):<{len(guild.text_channels)}}| {len(self.pins):<{4}} | {channel.name}", end="\n")
            try:
                channel_pins: AsyncIterable[discord.Message] = channel.pins()
                async for message in channel_pins:
                    await self.add_pin(message, connection=connection)
            except Exception as e:
                print(f"Failed to fetch pins from {channel.name}: {e}")