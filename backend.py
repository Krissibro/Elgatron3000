import discord
from discord import app_commands
import asyncio
from datetime import timedelta

async def annoy_internal(ctx, user: str, message: str, amount: int, interval: str):
    embed = discord.Embed(
        title = "Annoy",
        description=f"Started pinging {user} with\nMessage: {message}"
    )
    embed.add_field(name="Amount:", value=amount, inline=True)
    embed.add_field(name="Interval:", value=timedelta(seconds=interval), inline=True)
    await ctx.response.send_message(embed = embed)

    if user is None:
        await ctx.followup.send("User not found!")
        return
    
    try:
        for i in range(amount):
            await ctx.channel.send(f"{user} {message}")
            await asyncio.sleep(interval)
            
    except discord.Forbidden:
        # await c.send()("I don't have permission to send messages to that user!")
        await ctx.followup.send()("I don't have permission to send messages to that user!")



async def dm_aga_internal(ctx, message: str, amount: int, interval: str, client : discord.Client):
    pinged_user = await client.fetch_user(276441391502983170)
    print(f"Found user: {pinged_user.name}{pinged_user.discriminator}")

    embed = discord.Embed(
        title="DM Aga",
        description=f"Started annoying HA with \nMessage: {message}"
    )
    embed.add_field(name="Amount:", value=amount, inline=True)
    embed.add_field(name="Interval:", value=timedelta(seconds=interval), inline=True)
    await ctx.response.send_message(embed = embed)

    if pinged_user is None:
        await ctx.followup.send("User not found!")
        return
    
    try:
        for i in range(amount):
            await pinged_user.send(message)
            await asyncio.sleep(interval)
            
    except discord.Forbidden:
        await ctx.followup.send("I don't have permission to send messages to that user!")


async def get_attention_internal(ctx, user: str, message: str, amount: int, client : discord.Client):
    embed = discord.Embed(
        title="get_attention",
        description= f"Started pinging {user} with Message: {message}"
    )
    await ctx.response.send_message(embed = embed)

    if user is None:
        embed = discord.Embed(
            title="User not found!"
        )
        await ctx.followup.send(embed = embed)
        return

    for i in range(amount):
        message = await ctx.channel.send(f'''{user} {message} \nReact with \U0001F44D to stop being notified''')
        await message.add_reaction('\U0001F44D')

        def check(reaction, user):
            return user != client.user and reaction.message.id == message.id and str(reaction.emoji) == '\U0001F44D'

        try:
            await client.wait_for('reaction_add', check=check, timeout=60.0)
            await ctx.channel.send("Will stop bothering you now :pensive:")
            break
        except asyncio.TimeoutError:
            return