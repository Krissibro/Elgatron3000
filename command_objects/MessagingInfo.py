from utilities.shared import *
from command_objects.IInfo import *


class MessagingInfo(IInfo):
    def __init__(self, command: str, user: discord.User, message: str, amount: int, interval: int):
        self.command: str = command
        self.message: str = message
        self.amount: int = amount
        self.remaining: int = amount
        self.interval: int = interval
        self.user: str = "" if user is None else user.mention
        self.messages = []

    def make_embed(self):
        embed = discord.Embed(
            title=f"Command: {self.command}",
            description=f"Message: {self.message}"
        )
        embed.add_field(name="User:", value=f"{self.user}", inline=False)
        embed.add_field(name="Amount:", value=f"{self.remaining}/{self.amount}", inline=True)
        embed.add_field(name="Interval:", value=f"{timedelta(seconds=self.interval)}", inline=True)
        return embed

