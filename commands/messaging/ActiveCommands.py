import discord

from typing import List, Dict
from asyncio import Task

from commands.messaging.CommandInfo import CommandInfo


class ActiveCommands:
    def __init__(self):
        self.running_commands_dict: Dict[int, CommandInfo]  = {}

    def add_command(self, command: CommandInfo) -> int:
        command_id = max(self.running_commands_dict.keys(), default=0) + 1
        self.running_commands_dict[command_id] = command
        return command_id

    def get_ids(self) -> List[int]:
        return list(self.running_commands_dict.keys())

    def is_empty(self) -> bool:
        return not self.running_commands_dict

    def check_if_command_exists(self, command_id) -> bool:
        return command_id in self.running_commands_dict

    async def kill(self, command_id: int) -> None:
        await self.running_commands_dict[command_id].kill()

    def remove_command(self, command_id: int) -> None:
        del self.running_commands_dict[command_id]

    def make_overview_embed(self) -> discord.Embed:
        embed = discord.Embed(title="Showing all running processes:",
                              color=discord.Color.blue())

        for index, command in enumerate(self.running_commands_dict.values()):
            command.add_info_field(index+1, embed)

        return embed

    def make_dropdown_options(self) -> List[discord.SelectOption]:
        dropdown_options = []
        for index, (command_id, command_info) in enumerate(self.running_commands_dict.items()):
            option = discord.SelectOption(label=f"{index}:", 
                                          value=str(command_id), 
                                          description=command_info.get_select_description()
                                          )
            dropdown_options.append(option)
        return dropdown_options
    
    def get_command_embed(self, command_id) -> discord.Embed:
        embed = self[command_id].make_embed()
        return embed

    def __getitem__(self, index) -> CommandInfo:
        return self.running_commands_dict[index]
