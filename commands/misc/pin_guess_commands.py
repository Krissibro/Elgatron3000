from typing import AsyncIterable, List
import discord
import random
import pickle
import os

from discord import app_commands
from discord.ext import commands

from utilities.elgatron import Elgatron
from utilities.validators import validate_text_channel

from collections import namedtuple

# Pickle will not store the message object itself, so it had to be dumbed down to a namedtuple
Pin = namedtuple("Pin", ["author", "content", "attachments", "channel", "id"])


def make_pin(message: discord.Message) -> Pin:
    return Pin(message.author.display_name, message.content,
               [attachment.url for attachment in message.attachments],
               message.channel.id, message.id)


class PinManager:
    def __init__(self):
        self.pins: List[Pin] = []

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
        path = "./data/pins.pkl"
        if os.path.exists(path):
            with open(path, 'rb') as file:
                self.pins = pickle.load(file)

        print(f"Initialized with {len(self.pins)} pins")

    def save_pins(self) -> None:
        """Saves all the pins to the disk."""
        print(f"Saving {len(self.pins)} pins")
        with open("./data/pins.pkl", "wb") as file:
            pickle.dump(self.pins, file)


class PinView(discord.ui.View):
    def __init__(self, message_ctx, pin, timeout=10*60):
        super().__init__(timeout=timeout)
        self.pin: Pin = pin
        self.message_ctx: discord.Interaction = message_ctx

    async def make_first_embed(self) -> discord.Embed:
        """Creates the embed containing the title and the selected pin.
        Also appends the attachments if there are any"""
        embed: discord.Embed = discord.Embed(title="Guess the pin!",
                                             description=self.pin.content if self.pin.content else None)
        return embed

    async def make_sinner_embed(self) -> discord.Embed:
        embed: discord.Embed = await self.make_first_embed()
        embed.add_field(name="By",
                        value=f"{self.pin.author}", inline=True)
        # TODO guild id hardcoded, make dynamic
        embed.add_field(name="Context",
                        value=f"https://discord.com/channels/{self.message_ctx.guild_id}/{self.pin.channel}/{self.pin.id}")
        return embed

    async def send_attachments(self) -> None:
        """Sends the attachments of the pin to the channel if there are any."""
        channel = self.message_ctx.channel
        text_channel = validate_text_channel(channel)
        if isinstance(text_channel, discord.Embed):
            return

        if self.pin.attachments:
            await text_channel.send("\n".join(attachment for attachment in self.pin.attachments))

    async def reveal_author(self):
        """Method to reveal the author and edit the original message."""
        sinner_embed = await self.make_sinner_embed()
        await self.message_ctx.edit_original_response(embed=sinner_embed, view=None)

    async def on_timeout(self):
        # We might want to double-check here in case it times out exactly at the same time
        await self.reveal_author()

    @discord.ui.button(label="Reveal the sinner!", style=discord.ButtonStyle.success)
    async def reveal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.reveal_author()

class GuessThatPin(commands.GroupCog, group_name="pin"):
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        self.pin_manager: PinManager = PinManager()
        self.pin_manager.load_pins()

    @commands.Cog.listener('on_message_edit')
    async def on_message_edit(self, before, after):
        """Detects if a message has been edited.
        If a message is pinned, it is saved to the storage.
        If a message is unpinned, it is removed from storage"""

        # If pinned
        if not before.pinned and after.pinned:
            self.pin_manager.add_pin(after)

        # If unpinned
        if before.pinned and not after.pinned:
            self.pin_manager.remove_pin(after)

    @app_commands.command(
        name="guess",
        description="Guess the pin!",
    )
    async def guess_that_pin(self, ctx: discord.Interaction):
        if not self.pin_manager.pins:
            await ctx.response.send_message("No pinned messages found.")
            return

        pin = self.pin_manager.load_random_pin()

        view = PinView(ctx, pin)
        embed = await view.make_first_embed()

        await ctx.response.send_message(embed=embed, view=view)
        await view.send_attachments()

    @app_commands.command(
        name="sync",
        description="re-sync pins!",
    )
    async def sync_pins(self, ctx: discord.Interaction):
        await self.pin_manager.fetch_pins(self.bot)

        embed = discord.Embed(title=f"{len(self.pin_manager.pins)} pins were loaded!",)
        await ctx.response.send_message(embed=embed)

# Todo: handle if a pinned message is deleted or ehh?
# I assume we could just make it so that it re-syncs every time it connects? i dont think it's that demanding?

# Alternative method, but without the previous state of the message
# @client.event
# async def on_raw_message_edit(payload):
#     """Detects if any message has been edited.
#     If a message is pinned or have been pinned previously and just edited, it is detected."""
#     print(f"Edit detected")
#     if not client.get_channel(payload.channel_id):
#         return
#     if payload.data["pinned"]:
#         print("Get pinned")


async def setup(bot: Elgatron):
    await bot.add_cog(GuessThatPin(bot), guild=discord.Object(id=bot.guild_id))