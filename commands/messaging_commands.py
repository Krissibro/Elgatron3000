import discord
import asyncio

from discord import app_commands
from discord.ext import commands

from command_objects.Command import Command
from command_objects.MessagingInfo import MessagingInfo
from utilities.helper_functions import parse_time, validate_interval, validate_amount
from utilities.settings import guild_id


async def execute_command(ctx, command_name, internal_function, user: discord.User, message: str, amount: int, interval: int, channel: discord.TextChannel) -> None:
    """
    Executes a specified command with validation, tracking, and response handling.

    Args:
        ctx (Context): The context in which the command is being executed.
        command_name (str): The name of the command to be executed.
        internal_function (Coroutine): The asynchronous function representing the command's logic.
        user (discord.User): The Discord user who is targeted or involved in the command.
        message (str): A message associated with the command.
        amount (int): The amount of times a command is to be executed.
        interval (int): The time intervals for the command's operation.
        channel (discord.TextChannel): The channel in which the command is being executed.

    Description:
        This function validates user input, creates a command with necessary information, and tracks it using a command tracker.
        It sends an ephemeral response message with the command details, executes the command, and cleans up after completion.
        If validation fails at any step, the function exits without executing the command.
    """

    # Error handling
    if not (await validate_amount(ctx, amount) and await validate_interval(ctx, interval)):
        return

    # Create a Command object with the given information
    messaging_info = MessagingInfo(command_name, user, message, amount, interval, channel)
    async_task = asyncio.create_task(internal_function(ctx, messaging_info))
    command = Command(messaging_info, async_task)

    # Run the given command
    await ctx.response.send_message(embed=messaging_info.make_embed(), ephemeral=True, delete_after=10)
    await async_task

    # Clean up after Command
    command.end()


class ReactButton(discord.ui.View):
    seen: bool = False

    @discord.ui.button(emoji="🤨", style=discord.ButtonStyle.success)
    async def wake_up_bitch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.send("New death grips album dropping tomorrow :pensive:")
        await interaction.response.defer()
        self.seen = True
        self.stop()


async def get_attention_internal(ctx, command_info: MessagingInfo) -> None:
    while command_info.remaining > 0:
        command_info.remaining -= 1
        view = ReactButton(timeout=command_info.interval * 2)

        message = await ctx.channel.send(command_info.get_mention(),
                                         embed=discord.Embed(title=f"{command_info.message}"),
                                         view=view)

        command_info.add_message(message)

        await asyncio.sleep(command_info.interval)
        if view.seen:
            break

    await command_info.delete_messages()


async def dm_spam_internal(ctx, command_info: MessagingInfo) -> None:
    try:
        while command_info.remaining > 0:
            command_info.remaining -= 1
            await command_info.user.send(command_info.message)
            await asyncio.sleep(command_info.interval)

    except discord.Forbidden:
        await ctx.followup.send(embed=discord.Embed(title="I don't have permission to send messages to that user!"),
                                ephemeral=True)


async def annoy_internal(ctx, command_info: MessagingInfo) -> None:
    while command_info.remaining > 0:
        command_info.remaining -= 1
        message = await ctx.channel.send(f"{command_info.get_mention()} {command_info.message}")
        command_info.add_message(message)
        await asyncio.sleep(command_info.interval)

    await command_info.delete_messages()


class MessagingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="dm_spam",
        description="Annoy someone as many times as you would like with a given interval!",
    )
    async def dm_spam(self, ctx, user: discord.User, message: str, amount: int, interval: str):
        interval = parse_time(interval)
        await execute_command(ctx, "dm_spam", dm_spam_internal, user, message, amount, interval, ctx.channel)

    @app_commands.command(
        name="get_attention",
        description="Ping someone once every 10 seconds 100 times or until they react"
    )
    async def get_attention(self, ctx, user: discord.User, message: str = "WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP WAKE UP",
                            amount: int = 100, interval: str = "10s"):
        interval = parse_time(interval)
        await execute_command(ctx, "get_attention", get_attention_internal, user, message, amount, interval,
                              ctx.channel)

    @app_commands.command(
        name="annoy",
        description="Spam a message at someone!",
    )
    async def annoy(self, ctx, message: str, amount: int, interval: str, user: discord.User = None):
        interval = parse_time(interval)
        await execute_command(ctx, "annoy", annoy_internal, user, message, amount, interval, ctx.channel)


async def setup(bot):
    await bot.add_cog(MessagingCommands(bot), guild=bot.get_guild(guild_id))