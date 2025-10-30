import asyncio
from collections.abc import Callable
import discord

from datetime import timedelta
from typing import List, Union

from commands.messaging.CommandInfo import CommandInfo

from utilities.transformers import IntervalTranfsormer, PositiveIntTransformer
from utilities.helper_functions import char_to_emoji, format_seconds
from utilities.settings import active_commands

class MessagingInfo(CommandInfo):
    def __init__(self, internal_function: Callable, target: Union[discord.User, discord.Role, None], message: str, amount: int, interval: timedelta, channel: discord.TextChannel):
        self.message: str = message
        self.remaining: int = amount
        self.interval: timedelta = interval
        self.target: Union[discord.User, discord.Role, None] = target
        self.messages: List[discord.Message] = []

        self.process = asyncio.create_task(internal_function(self))
        self.command_id = active_commands.add_command(self)

        command_name = " ".join(internal_function.__name__.split('_')[:-1])
        super().__init__(command_name, channel)

    def make_embed(self):
        embed = discord.Embed(
            title=f"Command: {self.command_name}",
            description=f"Message: {self.message}"
        )
        if self.target is not None:
            embed.add_field(name="User:", value=f"{self.get_mention()}", inline=False)
        embed.add_field(name="Remaining:", value=f"{self.remaining}", inline=True)
        embed.add_field(name="Interval:", value=f"{self.interval}", inline=True)
        return embed

    def add_info_field(self, index: int, embed: discord.Embed) -> None:
        embed.add_field(name=f"{char_to_emoji(index)}: {self.command_name}",
                        value=f"{self.get_mention()}\n{self.message}",
                        inline=False)

    def make_select_option(self, index: int, command_id: int) -> discord.SelectOption:
        return discord.SelectOption(label=f"{index}:", value=str(command_id), description=f"{self.message}"[:100])

    async def kill(self) -> None:
        self.process.cancel()
        await self.delete_messages()

    def add_message(self, message: discord.Message) -> None:
        self.messages.append(message)

    async def delete_messages(self) -> None:
        await self.channel.delete_messages(self.messages[1:])

    def get_edit_window(self, interaction) -> discord.ui.Modal:
        return EditMessagingCommandWindow(interaction, self)

    def get_mention(self) -> str:
        return self.target.mention if self.target else ""

class EditMessagingCommandWindow(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, messaging_info: MessagingInfo) -> None:
        super().__init__(title="Edit")
        self.messaging_info: MessagingInfo = messaging_info
        self.original_response = interaction

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
            default=format_seconds(messaging_info.interval.seconds)
        )
        self.add_item(self.message_input)
        self.add_item(self.amount_input)
        self.add_item(self.interval_input)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        message = self.message_input.value
        interval = await IntervalTranfsormer().transform(interaction, self.interval_input.value)
        amount = await PositiveIntTransformer().transform(interaction, self.amount_input.value)

        if interaction.response.is_done():
            return
        
        await interaction.response.defer()
        self.messaging_info.message     = message
        self.messaging_info.remaining   = amount
        self.messaging_info.interval    = interval
        await self.original_response.edit_original_response(embed=self.messaging_info.make_embed())
