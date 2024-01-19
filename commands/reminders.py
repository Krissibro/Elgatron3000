

from command_objects.Command import *
from command_objects.ReminderInfo import *
from dateutil import *
from APScheduler import *
from utilities.helper_functions import parse_time


# async def execute_command(ctx, command_name, internal_function, user: discord.User, message: str, amount: int, interval: int, channel: discord.TextChannel):
#     # Error handling
#     if not (await validate_amount(ctx, amount) and await validate_interval(ctx, interval)):
#         return
#
#     # Create a Command object with the given information
#     messaging_info = ReminderInfo(command_name, user, message, amount, interval, channel)
#     async_task = asyncio.create_task(internal_function(ctx, messaging_info))
#     command = Command(messaging_info, async_task)
#
#     # Run the given command
#     await ctx.response.send_message(embed=messaging_info.make_embed(), ephemeral=True, delete_after=10)
#     await async_task
#
#     # Clean up after Command
#     command.end()


@tree.command(
    name="reminder",
    description="Create a reminder!",
    guild=discord.Object(id=guild_id)
)
async def reminder(ctx, message: str, time: str, date: str = None, repeat: str = "1", user: discord.User = None):
    # Error handling and parsing of user input

    # ChronTrigger

    # Schedule reminder_internal
    scheduler.add_job(reminder_internal, CronTrigger.from_crontab(f"0 {time} {date}"))


async def reminder_internal(ctx, command_info: ReminderInfo):
    while command_info.remaining > 0:
        command_info.remaining -= 1
        message = await ctx.channel.send(f"{command_info.user} {command_info.message}")
        command_info.add_message(message)
        await asyncio.sleep(command_info.interval)

    await command_info.delete_messages()