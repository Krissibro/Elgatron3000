from typing import Optional

import discord
import logging
import json

from tortoise import Tortoise
from pathlib import Path
from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.commands.messaging.ActiveCommands import ActiveCommands
from app.core.elgaTree import ElgaTree

class Elgatron(Bot):
    def __init__(self):
        with open("static/config.json", "r") as f:
            contents = json.load(f)

        self.guild_id = contents["guild"]
        self.testing = contents["testing"]
        self.game_channel_id = contents["game_channel_id"]
        self.wordle_channel_id = contents["wordle_channel_id"]
        self.testing_channel_id = contents["testing_channel_id"]

        self.scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone="Europe/Oslo")
        self.active_commands: ActiveCommands = ActiveCommands()

        self.logger = logging.getLogger("discord")

        super().__init__(intents=self.get_intents(), command_prefix="/", tree_cls=ElgaTree)

    async def setup_hook(self) -> None:
        path = Path("./app/commands").resolve()
        await Tortoise.init(
            db_url=f"sqlite://{path}",
            modules={"models": ["app.models"]}
        )
        await Tortoise.generate_schemas()

        await self.load_extension("./app/commands")

        self.scheduler.start()
        self.scheduler.print_jobs()

    async def on_ready(self):
        if self.testing:
            # discord.Object(id=...) is better than bot.get_guild(...) because it works when disconnected
            await self.tree.sync(guild=discord.Object(id=self.guild_id))

        print("Ready!")

    async def close(self) -> None:
        await Tortoise.close_connections()
        await super().close()

    async def load_extension(self, name: str, *, package: Optional[str] = None) -> None:
        path = Path(name)
        for file_path in path.glob("**/*_commands.py"):
            print(file_path)
            file_parts = file_path.parts

            if "the_lab" in file_parts and (not self.testing):
                continue

            formatted_path = ".".join(file_parts).strip(".py")
            try:
                await super().load_extension(name=formatted_path, package=package)
            except Exception as e:
                self.logger.error(f"Failed to load extension {name}.", exc_info=e)

    @staticmethod
    def get_intents():
        intents: discord.Intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        return intents