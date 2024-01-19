import datetime

from utilities.shared import *
from command_objects.CommandInfo import *
from utilities.helper_functions import char_to_emoji


class ReminderInfo(CommandInfo):
    # Command name
    # Message
    # Repeat, yes (forever), no (1), amount (2+)
    # Time: 00:00
    # Date: (optional) DD.MM
    def __init__(self, command_name: str, user: discord.User, message: str, time: datetime.time, date: datetime.date,
                 repeating_amount: int, channel: discord.TextChannel):
        super().__init__(channel)
        self.command_name: str = command_name
        self.message: str = message
        self.time: datetime.time = time
        self.date: datetime.date = date
        self.repeating_amount: int = repeating_amount
        self.remaining = self.repeating_amount
        self.user: str = "" if user is None else user.mention
        self.username: str = "" if user is None else user.name

    def make_embed(self):
        embed = discord.Embed(
            title=f"Command: {self.command_name}",
            description=f"Message: {self.message}"
        )
        embed.add_field(name="User:", value=f"{self.user}", inline=False)
        embed.add_field(name="Time:", value=f"{self.time}", inline=True)
        embed.add_field(name="Date:", value=f"{self.date}", inline=True) if self.date is not None else None
        embed.add_field(name="Repeating:", value=f"{self.remaining}/{self.repeating_amount}" if not self.repeating_amount == "yes"
                        else "Yes", inline=True)
        return embed

    def make_overview(self, index, embed):
        formatted_command_string = " ".join(self.command_name.split("_")).capitalize()
        embed.add_field(name=f"{char_to_emoji(index)} {formatted_command_string}",
                        value=f"{self.user}\n{self.message}",
                        inline=False)

        return embed

    def make_select_option(self, index):
        return discord.SelectOption(label=f"{index}:",
                                    value=str(index),
                                    description=f"{self.message}")
