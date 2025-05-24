import asyncio
from ast import literal_eval

import discord

from datetime import timedelta
from typing import List

from command_objects.CommandInfo import CommandInfo
from utilities.helper_functions import char_to_emoji, format_seconds, validate_numeric, validate_amount, \
    validate_interval, parse_time


class MessagingInfo(CommandInfo):
    def __init__(self, command_name: str, user: discord.User, message: str, amount: int, interval: int, channel: discord.TextChannel):
        super().__init__(command_name, channel)
        self.message: str = message
        self.amount: int = amount
        self.remaining: int = amount
        self.interval: int = interval
        self.user: discord.User = user
        self.messages: List[discord.Message] = []
        self.process = None

    def make_embed(self):
        embed = discord.Embed(
            title=f"Command: {self.command_name}",
            description=f"Message: {self.message}"
        )
        if self.user is not None:
            embed.add_field(name="User:", value=f"{self.get_mention()}", inline=False)
        embed.add_field(name="Amount:", value=f"{self.remaining}/{self.amount}", inline=True)
        embed.add_field(name="Interval:", value=f"{timedelta(seconds=self.interval)}", inline=True)
        return embed

    def make_overview(self, index, embed):
        embed.add_field(name=f"{char_to_emoji(index)} {self.command_name}",
                        value=f"{self.get_mention()}\n{self.message}",
                        inline=False)

        return embed

    def make_select_option(self, index):
        return discord.SelectOption(label=f"{index}:", value=str(index), description=f"{self.message}"[:100])

    def kill(self):
        self.process.cancel()

    def add_message(self, message):
        self.messages.append(message)

    async def delete_messages(self):
        await self.channel.delete_messages(self.messages[1:])

    def get_mention(self):
        return self.user.mention if self.user else ""

    def get_edit_window(self):
        return EditMessagingCommandWindow(self)

class EditMessagingCommandWindow(discord.ui.Modal):
    def __init__(self, messaging_info) -> None:
        super().__init__(title="Edit")
        self.messaging_info = messaging_info

        self.message_input = discord.ui.TextInput(
            label="Message:",
            style=discord.TextStyle.short,
            default=messaging_info.message
        )
        self.amount_input = discord.ui.TextInput(
            label="Amount:",
            style=discord.TextStyle.short,
            default=str(messaging_info.remaining)
        )
        self.interval_input = discord.ui.TextInput(
            label="Interval:",
            style=discord.TextStyle.short,
            default=format_seconds(messaging_info.interval)
        )
        self.add_item(self.message_input)
        self.add_item(self.amount_input)
        self.add_item(self.interval_input)

        self.finished_event = asyncio.Event()

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        if (
            not await validate_numeric(interaction, self.amount_input.value, "Amount must be numeric") or
            not await validate_amount(interaction, int(self.amount_input.value)) or
            not await validate_interval(interaction, parse_time(self.interval_input.value))
        ):
            self.stop()
            self.finished_event.set()
            return

        self.messaging_info.message = self.message_input.value
        self.messaging_info.amount = literal_eval(self.amount_input.value)
        self.messaging_info.remaining = literal_eval(self.amount_input.value)
        self.messaging_info.interval = parse_time(self.interval_input.value)

        self.stop()
        self.finished_event.set()  # Signal that the modal is closed