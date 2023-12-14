import discord

from utilities.shared import *
from command_objects.CommandInfo import *
from typing import List


class Command:
    running_commands_dict = {}

    def __init__(self, info: CommandInfo, task):
        self.id = self.assign_id()
        self.info = info
        self.process = task
        self.running_commands_dict[self.id] = self

    # Assigns the lowest ID
    def assign_id(self) -> int:
        i = 1
        while i in self.running_commands_dict.keys():
            i += 1
        return i

    @classmethod
    def get_ids(cls) -> List[int]:
        return list(cls.running_commands_dict.keys())

    def get_embed(self) -> discord.Embed:
        embed = self.info.make_embed()
        embed.add_field(name="ID:", value=f"{self.id}", inline=True)
        return embed

    @classmethod
    def get_embed_by_id(cls, command_id) -> discord.Embed:
        return cls.running_commands_dict[command_id].get_embed()

    def end(self) -> None:
        del self.running_commands_dict[self.id]

    def kill(self) -> None:
        self.process.cancel()
        del self.running_commands_dict[self.id]

    @classmethod
    def kill_all(cls) -> None:
        for command in cls.running_commands_dict.values():
            command.kill()

    @classmethod
    def get_command(cls, command_id):
        return cls.running_commands_dict[command_id]

    @classmethod
    def is_empty(cls):
        return not cls.running_commands_dict

    @classmethod
    def make_overview_embed(cls):
        # TODO beautify this embed
        embed = discord.Embed(title="Showing all running processes:")
        for (i, j) in cls.running_commands_dict.items():
            embed.add_field(name=f"{i}: {j.info.command}", value=j.info.user, inline=False)
        return embed
