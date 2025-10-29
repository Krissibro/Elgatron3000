import discord

from datetime import timedelta
from typing import List, Union

from commands.messaging.CommandInfo import CommandInfo

from utilities.transformers import IntervalTranfsormer, PositiveIntTransformer
from utilities.helper_functions import char_to_emoji, format_seconds
from utilities.validators import validate_natural_number, validate_interval

class MessagingInfo(CommandInfo):
    def __init__(self, command_name: str, target: Union[discord.User, discord.Role, None], message: str, amount: int, interval: timedelta, channel: discord.TextChannel):
        super().__init__(command_name, channel)
        self.message: str = message
        self.amount: int = amount
        self.remaining: int = amount
        self.interval: timedelta = interval
        self.target: Union[discord.User, discord.Role, None] = target
        self.messages: List[discord.Message] = []
        self.process = None

    def make_embed(self):
        embed = discord.Embed(
            title=f"Command: {self.command_name}",
            description=f"Message: {self.message}"
        )
        if self.target is not None:
            embed.add_field(name="User:", value=f"{self.get_mention()}", inline=False)
        embed.add_field(name="Amount:", value=f"{self.remaining}/{self.amount}", inline=True)
        embed.add_field(name="Interval:", value=f"{self.interval}", inline=True)
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
        return self.target.mention if self.target else ""

    def get_edit_window(self):
        return EditMessagingCommandWindow(self)

class EditMessagingCommandWindow(discord.ui.Modal):
    def __init__(self, messaging_info: MessagingInfo) -> None:
        super().__init__(title="Edit")
        self.messaging_info: MessagingInfo = messaging_info

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
        interval = await IntervalTranfsormer().transform(interaction, self.interval_input.value)
        amount = await PositiveIntTransformer().transform(interaction, self.amount_input.value)

        if interaction.response.is_done():
            return

        self.messaging_info.message = self.message_input.value
        self.messaging_info.amount = amount
        self.messaging_info.remaining = amount
        self.messaging_info.interval = interval

        self.stop()
