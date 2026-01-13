import discord
import random
import json
import os
import io

from typing import AsyncIterable, List, Optional, Tuple

from utilities.errors import ElgatronError
from utilities.elgatron import Elgatron

class Pin:
    def __init__(self, channel_id: int, message_id: int, content: str) -> None:
        self.channel_id: int = channel_id
        self.message_id: int = message_id
        self.content: str = content
        self.file_data: List[Tuple[bytes, str]] = []
        self.message: Optional[discord.Message] = None

    async def _fetch_message(self, bot: Elgatron) -> None:
        channel = await bot.fetch_channel(self.channel_id)
        if not isinstance(channel, discord.TextChannel):
            raise ElgatronError("Channel not found!")
        self.message = await channel.fetch_message(self.message_id)

    async def _fetch_files(self) -> None:
        self.file_data.clear()

        if self.message is None:
            return

        for attachment in self.message.attachments:
            data = await attachment.read()
            self.file_data.append((data, attachment.filename))

    def build_files(self) -> List[discord.File]:
        # rebuilding file data each time works for whatever reason
        return [
            discord.File(io.BytesIO(data), filename)
            for data, filename in self.file_data
        ]

    async def load_message(self, bot: Elgatron) -> None:
        await self._fetch_message(bot)
        await self._fetch_files()

class PinManager:
    def __init__(self):
        self.pins: List[Pin] = []
        self.state_file_path: str = "./data/pins.json"
        self.load_pins()

    async def load_random_pin(self) -> Pin:
        """Loads a random pin from the stored chunks."""
        return random.choice(self.pins)

    def add_pin(self, message: discord.Message, save=True) -> None:
        """Adds a pin to the storage."""
        self.pins.append(Pin(message.channel.id, message.id, message.content))
        if save:
            self.save_pins()

    def remove_pin(self, message: discord.Message, save=True) -> None:
        """Removes a pin from the storage."""
        self.pins.remove(Pin(message.channel.id, message.id, message.content))
        if save:
            self.save_pins()

    async def fetch_pins(self, bot: Elgatron) -> None:
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
                    self.add_pin(message, False)
            except Exception as e:
                print(f"Failed to fetch pins from {channel.name}: {e}")

        self.save_pins()

    @staticmethod
    def get_dict_of_data(pins: List[Pin]) -> dict:
        data = [(pin.channel_id, pin.message_id, pin.content) for pin in pins]
        return {"pins": data}

    @staticmethod
    def retrieve_data_from_dict(data: dict) -> List[Pin]:
        raw_pins = data.get("pins", [])
        pins = [Pin(pin[0], pin[1], pin[2]) for pin in raw_pins]
        return pins

    def save_pins(self) -> None:
        """Save the current state to a JSON file."""
        with open(self.state_file_path, 'w') as file:
            json.dump(self.get_dict_of_data(self.pins), file)

    def load_pins(self) -> None:
        """Load the state from a JSON file if it exists, otherwise set a new word."""
        if os.path.exists(self.state_file_path):
            with open(self.state_file_path, 'r') as file:
                data = json.load(file)
                self.pins = self.retrieve_data_from_dict(data)
