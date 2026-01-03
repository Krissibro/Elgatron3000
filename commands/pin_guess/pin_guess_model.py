import discord
import random
import pickle
import os

from collections import namedtuple

from typing import AsyncIterable, List

from utilities.elgatron import Elgatron

# Pickle will not store the message object itself, so it had to be dumbed down to a namedtuple
Pin = namedtuple("Pin", ["author", "content", "attachments", "channel_id", "message_id"])


def make_pin(message: discord.Message) -> Pin:
    return Pin(message.author.display_name,
               message.content,
               [attachment.url for attachment in message.attachments],
               message.channel.id,
               message.id
               )


class PinManager:
    def __init__(self):
        self.path = "./data/pins.pkl"
        self.pins: List[Pin] = []
        self.load_pins()

    def load_random_pin(self) -> Pin:
        """Loads a random pin from the stored chunks."""
        return random.choice(self.pins)

    def add_pin(self, message: discord.Message) -> None:
        """Adds a pin to the storage."""
        pinned_message: Pin = make_pin(message)
        self.pins.append(pinned_message)
        self.save_pins()

    def remove_pin(self, message: discord.Message) -> None:
        """Removes a pin from the storage."""
        pinned_message: Pin = make_pin(message)
        self.pins.remove(pinned_message)
        self.save_pins()

    async def fetch_pins(self, bot: Elgatron) -> None:
        self.pins = []
        guild = bot.get_guild(bot.guild_id)
        if guild is None:
            print("Guild not found!")
            return

        # Fetch pins from all channels
        for i, channel in enumerate(guild.text_channels):
            # Epic loading bar for fun
            print(f"|{(i * '#'):<{len(guild.text_channels)}}| {len(self.pins):<{4}} | {channel.name}", end="\n")

            try:
                channel_pins: AsyncIterable[discord.Message] = channel.pins()
                async for message_pin in channel_pins:
                    self.pins.append(make_pin(message_pin))
            except Exception as e:
                print(f"Failed to fetch pins from {channel.name}: {e}")

        self.save_pins()

    def load_pins(self):
        if os.path.exists(self.path):
            with open(self.path, 'rb') as file:
                self.pins = pickle.load(file)

        print(f"Initialized with {len(self.pins)} pins")

    def save_pins(self) -> None:
        print(f"Saving {len(self.pins)} pins")

        with open(self.path, "wb") as file:
            pickle.dump(self.pins, file)