import os
from dotenv import load_dotenv

# Commands from other files
from commands.epic_games_commands import schedule_post_free_games

from utilities.settings import testing, bot


# TODO: MAY RUN MORE THAN ONCE! :skull:
# TODO: Add more COGS!!!!!
@bot.event
async def on_ready():

    for file in os.listdir("commands"):
        if file.endswith(".py"):
            await bot.load_extension(f"commands.{file[:-3]}")

    if testing:
        for file in os.listdir("the_lab"):
            if file.endswith(".py"):
                await bot.load_extension(f"the_lab.{file[:-3]}")

    # TODO: move this to /epic_games_commands
    bot.loop.create_task(schedule_post_free_games())

    print("Ready!")


load_dotenv("token.env")
bot.run(os.getenv("TOKEN"))
