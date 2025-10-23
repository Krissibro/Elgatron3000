import os
from typing import Optional
from dotenv import load_dotenv

from utilities.settings import bot, scheduler


# TODO: MAY RUN MORE THAN ONCE! :skull:
@bot.event
async def on_ready():
    guild=bot.get_guild(bot.guild_id)

    if not bot.testing:
        await bot.tree.sync(guild=guild)

    scheduler.start()
    scheduler.print_jobs()

    print("Ready!")
    

load_dotenv("token.env")
token: Optional[str] = os.getenv("TOKEN")
bot.run(token)