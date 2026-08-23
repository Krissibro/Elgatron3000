import json
import logging
from pathlib import Path

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot
from tortoise import Tortoise

from app.commands.messaging.ActiveCommands import ActiveCommands
from app.core.elgaTree import ElgaTree


class Elgatron(Bot):
    def __init__(self):
        with open("app/static/config.json", "r") as f:
            contents = json.load(f)

        self.guild_id: int = contents["guild"] # we should move away from these and save them in a db or something
        self.testing: bool = contents["testing"]
        self.game_channel_id: int = contents["game_channel_id"]
        self.wordle_channel_id: int = contents["wordle_channel_id"]
        self.testing_channel_id: int = contents["testing_channel_id"]

        self.scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone="Europe/Oslo")
        self.active_commands: ActiveCommands = ActiveCommands()

        self.logger: logging.Logger = logging.getLogger("discord")

        self.db_path = Path("app/database/db.sqlite3").resolve()
        self.command_paths = Path("app/commands")
        self.emulator_path = Path("app/static/game_roms").resolve()
        self.wordle_path = Path("app/static/word_lists").resolve()

        super().__init__(
            intents=self.get_intents(),
            command_prefix="/",
            tree_cls=ElgaTree,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        await Tortoise.init(
            db_url=f"sqlite:///{self.db_path}", modules={"models": ["app.models"]}
        )
        await Tortoise.generate_schemas()

        await self.load_extension(str(self.command_paths))

        self.scheduler.start()
        self.scheduler.print_jobs()

    async def on_ready(self):
        if self.testing:
            await self.tree.sync(guild=discord.Object(id=self.guild_id))

        self.logger.info("Ready!")

    async def close(self) -> None:
        await Tortoise.close_connections()
        await super().close()

    async def load_extension(self, name: str, *, package: str | None = None) -> None:
        path = Path(name)
        for file_path in path.glob("**/*_commands.py"):
            file_parts = file_path.with_suffix("").parts

            if "the_lab" in file_parts and (not self.testing):
                continue

            formatted_path = ".".join(file_parts)
            try:
                await super().load_extension(name=formatted_path, package=package)
            except Exception as e:
                self.logger.error(f"Failed to load extension {name}.", exc_info=e)
                continue

    @staticmethod
    def get_intents():
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        intents.members = True

        return intents
