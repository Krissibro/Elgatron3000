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
        commands_to_kill = list(cls.running_commands_dict.values())
        for command in commands_to_kill:
            command.kill()

    @classmethod
    def get_command(cls, command_id):
        return cls.running_commands_dict[command_id]

    @classmethod
    def is_empty(cls):
        return not cls.running_commands_dict

    @classmethod
    def make_overview_embed(cls):
        embed = discord.Embed(title="Showing all running processes:",
                              color=discord.Color.red())

        for index, command in cls.running_commands_dict.items():
            embed = command.info.make_overview(index, embed)

        return embed

    @classmethod
    def make_dropdown_options(cls):
        return [command.info.make_select_option(index) for index, command in cls.running_commands_dict.items()]

    @classmethod
    def check_if_command_exists(cls, command_id):
        return command_id in cls.running_commands_dict.keys()
