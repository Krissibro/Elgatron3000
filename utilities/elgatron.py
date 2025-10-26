import discord

from glob import glob
from discord.ext.commands import Bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler

class Elgatron(Bot):
    def __init__(self, guild_id, testing):
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        intents.message_content = True
        intents.guilds = True

        self.guild_id = guild_id
        self.testing = testing

        self.scheduler = AsyncIOScheduler(timezone='Europe/Oslo')
        
        super().__init__(intents=intents, command_prefix="/")

    async def setup_hook(self) -> None:
        for path in glob("./commands/**/*_commands.py", recursive=True):
            # files are in the format: "./x/y.py" 
            # this turns it to: "x.y"
            formatted_path = path[2:-3].replace("/", ".")
            await self.load_extension(formatted_path)
        

        if self.testing:
            for path in glob("./the_lab/**/*_commands.py", recursive=True):
                formatted_path = path[2:-3].replace("/", ".")
                await self.load_extension(formatted_path)

        self.scheduler.start()
        self.scheduler.print_jobs()
        
        await super().setup_hook()

    async def on_ready(self):
        if self.testing:
            # discord.Object(id=...) is better than bot.get_guild(...) because it works when disconnected
            await self.tree.sync(guild=discord.Object(id=self.guild_id))

        print("Ready!")
