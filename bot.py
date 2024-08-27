import os
from dotenv import load_dotenv

# Commands from other files
from commands.epic_games_commands import schedule_post_free_games
from commands.sync import *

from utilities.settings import testing, bot


# TODO: MAY RUN MORE THAN ONCE! :skull:
# TODO: Add more COGS!!!!!
@bot.event
async def on_ready():
    await bot.load_extension("commands.wordle")
    await bot.load_extension("commands.random_commands")
    await bot.load_extension("commands.polls")
    await bot.load_extension("commands.help")
    await bot.load_extension("commands.emulator_commands")
    await bot.load_extension("commands.command_management")
    await bot.load_extension("commands.messaging_commands")
    await bot.load_extension("commands.epic_games_commands")
    await bot.load_extension("commands.guess_that_pin")

    if testing:
        await bot.load_extension("the_lab.test_commands")
        await bot.load_extension("the_lab.petting")

    # TODO: Remove these from on_ready
    # initiate scheduled items
    bot.loop.create_task(schedule_post_free_games())

    print("Ready!")


load_dotenv("token.env")
bot.run(os.getenv("TOKEN"))
