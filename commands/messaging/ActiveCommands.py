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

    def add_command(self, command: CommandInfo, async_task: Task) -> int:
        command.process = async_task
        command_id = self.assign_id()
        self.running_commands_dict[command_id] = command
        return command_id

    def make_overview_embed(self) -> discord.Embed:
        embed = discord.Embed(title="Showing all running processes:",
                              color=discord.Color.blue())

        for index, command in self.running_commands_dict.items():
            embed = command.make_overview(index, embed)

        return embed

    def make_dropdown_options(self) -> List[discord.SelectOption]:
        return [command_info.make_select_option(index) for index, command_info in self.running_commands_dict.items()]

    def get_command_embed(self, command_id) -> discord.Embed:
        embed = self[command_id].make_embed()
        embed.add_field(name="ID:", value=f"{command_id}", inline=True)
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
