import os
import discord
from typing import Optional
from dotenv import load_dotenv

from utilities.settings import bot, scheduler


# TODO: MAY RUN MORE THAN ONCE! :skull:
@bot.event
async def on_ready():

    scheduler.start()
    scheduler.print_jobs()

    if bot.testing:
        # discord.Object(id=...) is better than bot.get_guild(...) because it works when disconnected
        await bot.tree.sync(guild=discord.Object(id=bot.guild_id))

    print("Ready!")

load_dotenv("token.env")
token: Optional[str] = os.getenv("TOKEN")
bot.run(token)