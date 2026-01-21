import discord
import logging
import json

from glob import glob
from discord.app_commands import TransformerError
from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from commands.messaging.ActiveCommands import ActiveCommands
from utilities.errors import ElgatronError
from utilities.elgaTree import ElgaTree

def get_intents():
    intents: discord.Intents = discord.Intents.default()
    intents.members = True
    intents.messages = True
    intents.message_content = True
    intents.guilds = True

    return intents


class Elgatron(Bot):
    def __init__(self):
        with open("utilities/config.json", "r") as f:
            contents = json.load(f)

        self.guild_id = contents["guild"]
        self.testing = contents["testing"]
        self.game_channel_id = contents["game_channel_id"]
        self.wordle_channel_id = contents["wordle_channel_id"]
        self.testing_channel_id = contents["testing_channel_id"]

        self.scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone='Europe/Oslo')
        self.active_commands: ActiveCommands = ActiveCommands()

        self.logger = logging.getLogger("discord")

        super().__init__(intents=get_intents(), command_prefix="/", tree_cls=ElgaTree)

    async def setup_hook(self) -> None:
        # TODO do this with pathlib, and maybe move to elgaTree
        for path in glob("./commands/**/*_commands.py", recursive=True):
            # files are in the format: "./x/y.py"
            # this turns it to: "x.y"
            formatted_path = path[2:-3].replace("/", ".") # linux
            formatted_path = formatted_path.replace("\\", ".") # windows
            await self.load_extension(formatted_path)


        if self.testing:
            for path in glob("./the_lab/**/*_commands.py", recursive=True):
                formatted_path = path[2:-3].replace("/", ".")
                formatted_path = formatted_path.replace("\\", ".")
                await self.load_extension(formatted_path)

        self.scheduler.start()
        self.scheduler.print_jobs()

        # TODO init DB

    async def on_ready(self):
        if self.testing:
            # discord.Object(id=...) is better than bot.get_guild(...) because it works when disconnected
            await self.tree.sync(guild=discord.Object(id=self.guild_id))

        print("Ready!")
