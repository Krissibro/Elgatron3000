import discord

from abc import ABC, abstractmethod


class CommandInfo(ABC):
    @abstractmethod
    def __init__(self, command_name: str,  channel: discord.TextChannel):
        self.command_name = command_name
        self.channel = channel

    @abstractmethod
    def make_embed(self) -> discord.Embed:
        pass

    @abstractmethod
    def add_info_field(self, index: int, embed: discord.Embed) -> None:
        pass
    
    @abstractmethod
    def get_select_description(self) -> str:
        pass

    @abstractmethod
    def get_edit_window(self, interaction) -> discord.ui.Modal:
        pass

    @abstractmethod
    async def kill(self) -> None:
        pass
