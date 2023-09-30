import discord
from discord import app_commands

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


running_commands_dict = {}


class Command:
    current_ids = set()

    def __init__(self, embed, task):
        self.id = self.assign_id()
        self.embed = embed
        self.process = task
        embed.add_field(name="ID:", value=f"{id}", inline=True)

    # Assigns the lowest ID
    def assign_id(self):
        i = 1
        while i in Command.current_ids:
            i += 1
        Command.current_ids.add(i)
        return i

    def kill(self):
        self.process.cancel()
        Command.current_ids.remove(self.id)