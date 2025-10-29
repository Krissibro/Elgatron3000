from datetime import timedelta
import discord
import asyncio

from commands.messaging.MessagingInfo import MessagingInfo
from typing import Callable, Union 

from utilities.settings import active_commands

async def execute_command(ctx, internal_function: Callable, target: Union[discord.User, discord.Role, None], message: str, amount: int, interval: timedelta, channel: discord.TextChannel) -> None:
    """
    Executes a specified command with validation, tracking, and response handling.

    Args:
        ctx (Context): The context in which the command is being executed.
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

    # Create a Command object with the given information
    function_name = " ".join(internal_function.__name__.split('_')[:-1])
    messaging_info = MessagingInfo(function_name, target, message, amount, interval, channel)

    async_task = asyncio.create_task(internal_function(ctx, messaging_info))
    command_id = active_commands.add_command(messaging_info, async_task)

    # Run the given command
    await ctx.response.send_message(embed=messaging_info.make_embed(), ephemeral=True, delete_after=10)
    await async_task

    # Clean up after Command
    active_commands.kill(command_id)


class ReactButton(discord.ui.View):
    @discord.ui.button(emoji="🤨", style=discord.ButtonStyle.success)
    async def wake_up_bitch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("New death grips album dropping tomorrow :pensive:")
        self.stop()


async def get_attention_internal(ctx, messaging_info: MessagingInfo) -> None:
    while messaging_info.remaining > 0:
        messaging_info.remaining -= 1

        mention = messaging_info.get_mention()
        button = ReactButton(timeout=messaging_info.interval.seconds * 2)
        embed = discord.Embed(title=f"{messaging_info.message}")

        message = await ctx.channel.send(mention, embed=embed, view=button)
        messaging_info.add_message(message) # message added to list so that it can be deleted in the future.

        await asyncio.sleep(messaging_info.interval.seconds)
        if button.is_finished():
            break

    await messaging_info.delete_messages()


async def dm_spam_internal(ctx, messaging_info: MessagingInfo) -> None:
    try:
        # these two should technically never happen 
        if isinstance(messaging_info.target, discord.Role):
            raise ValueError("Target user is invalid.")
        if messaging_info.target is None:
            raise ValueError("Target user is invalid.")
        
        while messaging_info.remaining > 0:
            messaging_info.remaining -= 1

            await messaging_info.target.send(messaging_info.message)
            await asyncio.sleep(messaging_info.interval.seconds)
    except ValueError:
        embed = discord.Embed(title="Can only message Users.")
        await ctx.followup.send(embed=embed, ephemeral=True)
    except discord.Forbidden:
        embed = discord.Embed(title="I don't have permission to send messages to that user.")
        await ctx.followup.send(embed=embed, ephemeral=True)
    except AttributeError:
        embed = discord.Embed(title="Unable to message a bot user.")
        await ctx.followup.send(embed=embed, ephemeral=True)

async def annoy_internal(ctx, messaging_info: MessagingInfo) -> None:
    while messaging_info.remaining > 0:
        messaging_info.remaining -= 1

        message = await ctx.channel.send(f"{messaging_info.get_mention()} {messaging_info.message}")
        messaging_info.add_message(message)

        await asyncio.sleep(messaging_info.interval.seconds)

    await messaging_info.delete_messages()