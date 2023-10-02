import discord
from datetime import timedelta
import asyncio

from utils.shared import *



@tree.command(
    name="annoy",
    description="Spam a message at someone!",
    guild=discord.Object(id=508383744336461842)
)
async def annoy(ctx, user: str, message: str, amount: int, interval: str):
    interval = eval(interval)

    if user is None:
        await ctx.response.send_message(embed = discord.Embed(title="User could not be found"), ephemeral = True)
        return
    if interval <= 0:
        await ctx.response.send_message(embed = discord.Embed(title="Interval cannot be less than or equal to 0"), ephemeral = True)
        return
    if amount <= 0:
        await ctx.response.send_message(embed = discord.Embed(title="Amount cannot be less than or equal to 0"), ephemeral = True)
        return

    comm_inf = Command_Info("Annoy", user, message, amount, interval)
    command = asyncio.create_task(annoy_internal(ctx, comm_inf))

    command_tracker = Command(comm_inf, command)
    running_commands_dict[command_tracker.id] = command_tracker

    await command

    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)


async def annoy_internal(ctx, comm_inf: Command_Info):
    await ctx.response.send_message(embed=comm_inf.make_embed(), ephemeral = True)

    try:
        for i in range(comm_inf.amount, 0, -1):
            comm_inf.amount = i
            await ctx.channel.send(f"{comm_inf.user} {comm_inf.message}")
            await asyncio.sleep(comm_inf.interval)

    except discord.Forbidden:
        await ctx.followup.send(embed=discord.Embed(title="I don't have permission to send messages to that user!"))



@tree.command(
    name="dm_aga",
    description="Annoy HA as many times as you would like with a given interval!",
    guild=discord.Object(id=508383744336461842)
)
async def dm_aga(ctx, message: str, amount: int, interval: str):
    interval = eval(interval)
    user = await client.fetch_user(276441391502983170)

    if user is None:
        await ctx.response.send_message(embed=discord.Embed(title="User not found!"), ephemeral = True)
        return
    if interval <= 0:
        await ctx.response.send_message(embed = discord.Embed(title="Interval cannot be less than or equal to 0"), ephemeral = True)
        return
    if amount <= 0:
        await ctx.response.send_message(embed = discord.Embed(title="Amount cannot be less than or equal to 0"), ephemeral = True)
        return

    comm_inf = Command_Info("DM Aga", user, message, amount, interval)
    command = asyncio.create_task(dm_spam_internal(ctx, comm_inf))

    command_tracker = Command(comm_inf, command)
    running_commands_dict[command_tracker.id] = command_tracker
    await command

    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)


async def dm_spam_internal(ctx, comm_inf: Command_Info):
    await ctx.response.send_message(embed=comm_inf.make_embed(), ephemeral = True)

    try:
        for i in range(comm_inf.amount, 0, -1):
            comm_inf.amount = i
            await comm_inf.user.send(comm_inf.message)
            await asyncio.sleep(comm_inf.interval)

    except discord.Forbidden:
        await ctx.followup.send(embed=discord.Embed(title="I don't have permission to send messages to that user!"), ephemeral = True)



@tree.command(
    name="get_attention",
    description="Ping someone x times, once every 60 seconds till they react",
    guild=discord.Object(id=508383744336461842)
)
async def get_attention(ctx, user: str, message: str, amount: int, interval: str):
    interval = eval(interval)

    if user is None:
        await ctx.response.send_message(embed = discord.Embed(title="User not found"), ephemeral = True)
        return
    if interval <= 0:
        await ctx.response.send_message(embed = discord.Embed(title="Interval cannot be less than or equal to 0"), ephemeral = True)
        return
    if amount <= 0:
        await ctx.response.send_message(embed = discord.Embed(title="Amount cannot be less than or equal to 0"), ephemeral = True)
        return

    comm_inf = Command_Info("Get Attention", user, message, amount, interval)
    command = asyncio.create_task(get_attention_internal(ctx, comm_inf, client))

    command_tracker = Command(comm_inf, command)
    running_commands_dict[command_tracker.id] = command_tracker

    await command

    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)


async def get_attention_internal(ctx, comm_inf: Command_Info, client: discord.Client):
    await ctx.response.send_message(embed=comm_inf.make_embed(), ephemeral = True)

    for i in range(comm_inf.amount, 0, -1):
        comm_inf.amount = i
        message = await ctx.channel.send(f"{comm_inf.user}",
            embed=discord.Embed(
                                title=f"{comm_inf.message}",
                                description="React with \U0001F44D to stop being notified"))
        await message.add_reaction('\U0001F44D')

        def check(reaction, user):
            return user != client.user and reaction.message.id == message.id and str(reaction.emoji) == '\U0001F44D'

        try:
            await client.wait_for('reaction_add', check=check, timeout=comm_inf.interval)
            await ctx.channel.send(embed=discord.Embed(title="Will stop bothering you now :pensive:"))
            break
        except asyncio.TimeoutError:
            continue