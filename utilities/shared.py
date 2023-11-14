import discord
from discord import app_commands
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import timedelta

from utilities.settings import guild_id


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

scheduler = AsyncIOScheduler(timezone='Europe/Oslo')

running_commands_dict = {}


class MessagingInfo:
    current_ids = set()

    def __init__(self, command: str, user: discord.User, message: str, amount:int, interval: int):
        self.command: str = command
        self.message: str = message
        self.amount: int = amount
        self.remaining: int = amount
        self.interval : int = interval
        self.user: str = "" if user is None else user.mention
        self.messages = []
    
    def make_embed(self):
        embed = discord.Embed(
            title= f"Command: {self.command}",
            description=f"Message: {self.message}"
        )
        embed.add_field(name="User:", value=f"{self.user}", inline=False)
        embed.add_field(name="Amount:", value=f"{self.remaining}/{self.amount}", inline=True)
        embed.add_field(name="Interval:", value=f"{timedelta(seconds=self.interval)}", inline=True)
        return embed


class Command:
    current_ids = set()

    def __init__(self, info: MessagingInfo, task):
        self.id = self.assign_id()
        self.info = info
        self.process = task

    # Assigns the lowest ID
    def assign_id(self):
        i = 1
        while i in self.current_ids:
            i += 1
        self.current_ids.add(i)
        return i

    def get_embed(self):
        embed = self.info.make_embed()
        embed.add_field(name="ID:", value=f"{self.id}", inline=True)
        return embed

    def kill(self):
        self.process.cancel()
        Command.current_ids.remove(self.id)
