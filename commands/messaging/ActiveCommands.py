import discord

from typing import List, Dict
from asyncio import Task

from commands.messaging.CommandInfo import CommandInfo


class ActiveCommands:
    def __init__(self):
        self.running_commands_dict: Dict[int, CommandInfo]  = {}

    # Assigns the lowest ID
    def assign_id(self) -> int:
        i = 1
        while i in self.running_commands_dict.keys():
            i += 1
        return i

    def add_command(self, command: CommandInfo) -> int:
        command_id = self.assign_id()
        self.running_commands_dict[command_id] = command
        return command_id

    def make_overview_embed(self) -> discord.Embed:
        embed = discord.Embed(title="Showing all running processes:",
                              color=discord.Color.blue())

        for index, command in enumerate(self.running_commands_dict.values()):
            command.add_info_field(index+1, embed)

        return embed

    def make_dropdown_options(self) -> List[discord.SelectOption]:
        dropdown_options = []
        for index, (command_id, command_info) in enumerate(self.running_commands_dict.items()):
            dropdown_options.append(command_info.make_select_option(index+1, command_id))
        return dropdown_options
    
    def get_command_embed(self, command_id) -> discord.Embed:
        embed = self[command_id].make_embed()
        return embed

    def get_ids(self) -> List[int]:
        return list(self.running_commands_dict.keys())

    def kill(self, command_id: int) -> None:
        self[command_id].kill()
        del self.running_commands_dict[command_id]

    def is_empty(self) -> bool:
        return not self.running_commands_dict

    def check_if_command_exists(self, command_id) -> bool:
        return command_id in self.running_commands_dict

    def __getitem__(self, index) -> CommandInfo:
        return self.running_commands_dict[index]
