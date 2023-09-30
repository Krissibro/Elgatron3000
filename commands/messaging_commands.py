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
        await ctx.followup.send(embed = discord.Embed(title="User could not be found"), delete_after=3, ephemeral = True)
        return
    if interval <= 0:
        await ctx.followup.send(embed = discord.Embed(title="Interval cannot be less than or equal to 0"), delete_after=3, ephemeral = True)
        return
    if amount <= 0:
        await ctx.followup.send(embed = discord.Embed(title="amount cannot be less than or equal to 0"), delete_after=3, ephemeral = True)
        return

    command = asyncio.create_task(annoy_internal(ctx, user, message, amount, interval))

    embed = discord.Embed(
        title="Command: Annoy",
        description=f"Message: {message}"
    )
    embed.add_field(name="User:", value=f"{user}", inline=False)
    embed.add_field(name="Amount:", value=f"{amount}", inline=False)
    embed.add_field(name="Interval:", value=f"{timedelta(seconds=interval)}", inline=False)

    command_tracker = Command(embed, command)
    running_commands_dict[command_tracker.id] = command_tracker

    await command

    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)


async def annoy_internal(ctx, user: str, message: str, amount: int, interval: int):
    embed = discord.Embed(
        title="Annoy",
        description=f"Started pinging {user} with\nMessage: {message}"
    )
    embed.add_field(name="Amount:", value=amount, inline=True)
    embed.add_field(name="Interval:", value=timedelta(seconds=interval), inline=True)
    await ctx.response.send_message(embed=embed, ephemeral = True)

    try:
        for i in range(amount):
            await ctx.channel.send(f"{user} {message}")
            await asyncio.sleep(interval)

    except discord.Forbidden:
        # await c.send()("I don't have permission to send messages to that user!")
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
        await ctx.followup.send(embed=discord.Embed(title="User not found!"), delete_after=3, ephemeral = True)
        return
    if interval <= 0:
        await ctx.followup.send(embed = discord.Embed(title="Interval cannot be less than or equal to 0"), delete_after=3, ephemeral = True)
        return
    if amount <= 0:
        await ctx.followup.send(embed = discord.Embed(title="amount cannot be less than or equal to 0"), delete_after=3, ephemeral = True)
        return

    command = asyncio.create_task(dm_spam_internal(ctx, user, message, amount, interval, client))

    embed = discord.Embed(
        title="Command: DM Aga",
        description=f"Message: {message}"
    )
    embed.add_field(name="Amount:", value=f"{amount}", inline=False)
    embed.add_field(name="Interval:", value=f"{timedelta(seconds=interval)}", inline=False)

    command_tracker = Command(embed, command)
    running_commands_dict[command_tracker.id] = command_tracker
    await command

    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)


async def dm_spam_internal(ctx, user: str, message: str, amount: int, interval: int, client: discord.Client):
    embed = discord.Embed(
        title="DM Aga",
        description=f"Started annoying HA with \nMessage: {message}"
    )
    embed.add_field(name="Amount:", value=amount, inline=True)
    embed.add_field(name="Interval:", value=timedelta(seconds=interval), inline=True)

    await ctx.response.send_message(embed=embed, ephemeral = True)

    try:
        for i in range(amount):
            await user.send(message)
            await asyncio.sleep(interval)

    except discord.Forbidden:
        await ctx.followup.send(embed=discord.Embed(title="I don't have permission to send messages to that user!"))



@tree.command(
    name="get_attention",
    description="Ping someone x times, once every 60 seconds till they react",
    guild=discord.Object(id=508383744336461842)
)
async def get_attention(ctx, user: str, message: str, amount: int, interval: str):
    interval = eval(interval)

    if user is None:
        await ctx.followup.send(embed = discord.Embed(title="User not found"), delete_after=3, ephemeral = True)
        return
    if interval <= 0:
        await ctx.followup.send(embed = discord.Embed(title="Interval cannot be less than or equal to 0"), delete_after=3, ephemeral = True)
        return
    if amount <= 0:
        await ctx.followup.send(embed = discord.Embed(title="amount cannot be less than or equal to 0"), delete_after=3, ephemeral = True)
        return

    command = asyncio.create_task(get_attention_internal(ctx, user, message, amount, interval, client))

    embed = discord.Embed(
        title="Command: Annoy",
        description=f"Message: {message}"
    )
    embed.add_field(name="User:", value=f"{user}", inline=False)
    embed.add_field(name="Amount:", value=f"{amount}", inline=False)

    command_tracker = Command(embed, command)
    running_commands_dict[command_tracker.id] = command_tracker

    await command

    del running_commands_dict[command_tracker.id]
    Command.current_ids.remove(command_tracker.id)


async def get_attention_internal(ctx, user: str, msg: str, amount: int, interval:int, client: discord.Client):
    embed = discord.Embed(
        title="Get attention",
        description=f"Started pinging {user} with Message: {msg}"
    )
    embed.add_field(name="User:", value=f"{user}", inline=False)
    embed.add_field(name="Amount:", value=f"{amount}", inline=False)
    embed.add_field(name="Interval:", value=f"{timedelta(seconds=interval)}", inline=False)
    await ctx.response.send_message(embed=embed, ephemeral = True)

    for i in range(amount):
        message = await ctx.channel.send(f"{user}",
            embed=discord.Embed(
                                title=f"{msg}",
                                description="React with \U0001F44D to stop being notified"))
        await message.add_reaction('\U0001F44D')

        def check(reaction, user):
            return user != client.user and reaction.message.id == message.id and str(reaction.emoji) == '\U0001F44D'

        try:
            await client.wait_for('reaction_add', check=check, timeout=interval)
            await ctx.channel.send(embed=discord.Embed(title="Will stop bothering you now :pensive:"))
            break
        except asyncio.TimeoutError:
            continue