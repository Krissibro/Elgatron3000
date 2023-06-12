import discord
from discord import app_commands
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(
    name="dm_ha",
    description="ping HA as many times as you would like with a given interval!",
    guild=discord.Object(id=508383744336461842)
)
async def dm_ha(ctx, message: str, amount: int, interval: str):
    pinged_user = await client.fetch_user(276441391502983170)

    print(f"Found user: {pinged_user.name}{pinged_user.discriminator}")

    await ctx.response.send_message(
        f"Started pinging HA with \nMessage: '{message}'\nAmount {amount} times \nInterval: {eval(interval)} seconds")

    if pinged_user is None:
        await ctx.followup.send("User not found!")
        return
    try:
        for i in range(amount):
            await pinged_user.send(message)
            await asyncio.sleep(eval(interval))
    except discord.Forbidden:
        await ctx.followup.send("I don't have permission to send messages to that user!")


@tree.command(
    name="prank",
    description="spam a message at someone!",
    guild=discord.Object(id=508383744336461842)
)
async def prank(ctx, user: str, message: str, amount: int, interval: str):
    await ctx.response.send_message(
        f"Started pinging {user} with \nMessage: '{message}'\nAmount {amount} times \nInterval: {eval(interval)} seconds")

    if user is None:
        await ctx.followup.send("User not found!")
        return
    try:
        for i in range(amount):
            await ctx.followup.send(f"{user} {message}")
            await asyncio.sleep(eval(interval))
    except discord.Forbidden:
        await ctx.followup.send()("I don't have permission to send messages to that user!")


@tree.command(
    name="get_attention",
    description="get someones attention!",
    guild=discord.Object(id=508383744336461842)
)
async def get_attention(ctx, user: str, text: str, interval: str):
    await ctx.response.send_message(
        f"Started pinging {user} with \nMessage: '{text}'\nInterval: {eval(interval)} minutes")

    if user is None:
        await ctx.followup.send("User not found!")
        return

    for i in range(10):
        message = await ctx.followup.send(f"react with \U0001F44D to stop being notified\n```{text}{user}```")
        await message.add_reaction('\U0001F44D')

        def check(reaction, user):
            return user != client.user and reaction.message.id == message.id and str(reaction.emoji) == '\U0001F44D'

        try:
            await client.wait_for('reaction_add', check=check, timeout=60.0 * eval(interval))
            await ctx.followup.send("Will stop bothering you now :)")
            break
        except asyncio.TimeoutError:
            return


@tree.command(
    name="pls_help",
    description="bot info!",
    guild=discord.Object(id=508383744336461842)
)
async def pls_help(ctx):
    await ctx.response.send_message('''
/prank <user> "<message>" <amount> <interval>
/dm_HA "<message>" <amount> <interval>

<interval> is in seconds, and can be evaluated by for example 20*60
''')


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=508383744336461842))
    print("Ready!")


# bot.run("token")
client.run(os.getenv("TOKEN"))
