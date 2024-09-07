import os
from dotenv import load_dotenv

from utilities.settings import testing, bot, guild_id, scheduler


# TODO: MAY RUN MORE THAN ONCE! :skull:
@bot.event
async def on_ready():

    for file in os.listdir("commands"):
        if file.endswith(".py"):
            await bot.load_extension(f"commands.{file[:-3]}")

    if testing:
        for file in os.listdir("the_lab"):
            if file.endswith(".py"):
                await bot.load_extension(f"the_lab.{file[:-3]}")

    if not testing:
        await bot.tree.sync(guild=bot.get_guild(guild_id))

    scheduler.start()
    scheduler.print_jobs()

    print("Ready!")


load_dotenv("token.env")
bot.run(os.getenv("TOKEN"))
