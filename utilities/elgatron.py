from glob import glob
import discord
from discord.ext.commands import Bot

class Elgatron(Bot):
    def __init__(self, guild_id, testing):
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        intents.message_content = True
        intents.guilds = True

        self.guild_id = guild_id
        self.testing = testing
        
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

        await super().setup_hook()