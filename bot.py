import os
from typing import Optional
from dotenv import load_dotenv
import glob

from utilities.settings import testing, bot, guild_id, scheduler


# TODO: MAY RUN MORE THAN ONCE! :skull:
@bot.event
async def on_ready():

    for path in glob.glob("./commands/**/*_c.py", recursive=True):
        # files are in the format: "./x/y.py" 
        # this turns it to: "x.y"
        formatted_path = path[2:-3].replace("/", ".")
        await bot.load_extension(formatted_path)
        

    if testing:
        for path in glob.glob("./the_lab/**/*_c.py", recursive=True):
            formatted_path = path[2:-3].replace("/", ".")
            await bot.load_extension(formatted_path)

    guild=bot.get_guild(guild_id)

    if not testing:
        await bot.tree.sync(guild=guild)

    scheduler.start()
    scheduler.print_jobs()

    print("Ready!")
    

load_dotenv("token.env")
token: Optional[str] = os.getenv("TOKEN")
bot.run(token)