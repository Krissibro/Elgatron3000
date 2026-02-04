import discord

from datetime import datetime, timedelta
from typing import Awaitable, Callable, Optional, Union, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from app.commands.messaging.ActiveCommands import ActiveCommands
from app.commands.messaging.CommandInfo import CommandInfo
from app.utilities.helper_functions import char_to_emoji, format_seconds
from app.utilities.transformers import IntervalTransformer, PositiveIntTransformer

class MessagingInfo(CommandInfo):
    def __init__(self,
                 internal_function: Callable[["MessagingInfo"], Awaitable[None]],
                 target: Union[discord.User, discord.Role, None], 
                 message: str, 
                 amount: int, 
                 channel: discord.TextChannel, 
                 start_time: datetime,  
                 interval: timedelta,
                 scheduler: AsyncIOScheduler,
                 active_commands: ActiveCommands
                 ):
        command_name = " ".join(internal_function.__name__.split('_')[:-1])
        super().__init__(command_name, channel, active_commands)

        self.message: str = message
        self.remaining: int = amount
        self.target: Union[discord.User, discord.Role, None] = target
        self.messages: List[discord.Message] = []

        self.internal_function: Callable[["MessagingInfo"], Awaitable[None]] = internal_function
        self.current_trigger = start_time
        self.interval: timedelta = interval
        self.scheduler = scheduler
        self.job_id = f"message_scheduler_{self.command_id}"

    def start_job(self) -> None:
        trigger = DateTrigger(self.current_trigger, timezone='Europe/Oslo')
        self.scheduler.add_job(
            self.run_command, 
            trigger=trigger, 
            id=self.job_id
        )

    async def run_command(self) -> None:
        await self.internal_function(self)
        self.remaining -= 1
        
        if self.remaining <= 0:
            await self.kill()
            return

        self.current_trigger += self.interval
        self.scheduler.add_job(
            self.run_command,
            trigger=DateTrigger(self.current_trigger, timezone="Europe/Oslo"),
            id=self.job_id,
            replace_existing=True
        )

    def get_mention(self) -> str:
        return self.target.mention if self.target else ""
    
    def add_message(self, message: discord.Message) -> None:
        self.messages.append(message)

    async def delete_messages(self) -> None:
        await self.channel.delete_messages(self.messages[1:])

    def make_embed(self) -> discord.Embed:
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
    
    def get_select_description(self) -> str:
        return self.message

    def get_edit_window(self, interaction) -> discord.ui.Modal:
        return EditMessagingCommandWindow(interaction, self)

    async def kill(self) -> None:
        self.active_commands.remove_command(self.command_id)
        if self.scheduler.get_job(self.job_id) is not None:
            self.scheduler.remove_job(job_id=self.job_id)

        await self.delete_messages()
        
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
        message: str = self.message_input.value
        interval: Optional[timedelta] = await IntervalTransformer().transform(interaction, self.interval_input.value)
        amount: Optional[int] = await PositiveIntTransformer().transform(interaction, self.amount_input.value)

        if interaction.response.is_done() or amount is None or interval is None:
            return
        
        await interaction.response.defer()
        self.messaging_info.message     = message
        self.messaging_info.remaining   = amount
        self.messaging_info.interval    = interval
        await self.original_response.edit_original_response(embed=self.messaging_info.make_embed())
