from utilities.shared import *
from command_objects.CommandInfo import *
from utilities.helper_functions import char_to_emoji


class MessagingInfo(CommandInfo):
    def __init__(self, command: str, user: discord.User, message: str, amount: int, interval: int, channel: discord.TextChannel):
        super().__init__(channel)
        self.command: str = command
        self.message: str = message
        self.amount: int = amount
        self.remaining: int = amount
        self.interval: int = interval
        self.user: str = "" if user is None else user.mention
        self.username: str = "" if user is None else user.name

    def make_embed(self):
        embed = discord.Embed(
            title=f"Command: {self.command}",
            description=f"Message: {self.message}"
        )
        embed.add_field(name="User:", value=f"{self.user}", inline=False)
        embed.add_field(name="Amount:", value=f"{self.remaining}/{self.amount}", inline=True)
        embed.add_field(name="Interval:", value=f"{timedelta(seconds=self.interval)}", inline=True)
        return embed

    def make_overview(self, index, embed):
        formatted_command_string = " ".join(self.command.split("_")).capitalize()
        embed.add_field(name=f"{char_to_emoji(index)} {formatted_command_string}",
                        value=f"{self.user}\n{self.message}",
                        inline=False)

        return embed

    def make_select_option(self, index):
        return discord.SelectOption(label=f"{index}:",
                                    value=str(index),
                                    description=f"{self.message}")
