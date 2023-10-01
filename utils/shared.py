import discord
from discord import app_commands
from datetime import timedelta

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


running_commands_dict = {}

class Command_Info():
    current_ids = set()

    def __init__(self, command: str, user: str, message: str, amount:int, interval: int):
        self.command = command
        self.message = message
        self.amount = amount
        self.interval = interval
        self.user = user
    
    def make_embed(self):
        embed = discord.Embed(
            title= f"Command: {self.command}",
            description=f"Message: {self.message}"
        )
        embed.add_field(name="User:", value=f"{self.user}", inline=False)
        embed.add_field(name="Amount:", value=f"{self.amount}", inline=False)
        embed.add_field(name="Interval:", value=f"{timedelta(seconds=self.interval)}", inline=False)
        return embed

class Command:
    current_ids = set()

    def __init__(self, info: Command_Info, task):
        self.id = self.assign_id()
        self.info = info
        self.process = task

    # Assigns the lowest ID
    def assign_id(self):
        i = 1
        while i in Command.current_ids:
            i += 1
        Command.current_ids.add(i)
        return i

    def get_embed(self):
        embed = self.info.make_embed()
        embed.add_field(name="ID:", value=f"{self.id}", inline=True)
        return embed

    def kill(self):
        self.process.cancel()
        Command.current_ids.remove(self.id)
