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
    def make_overview(self, index, embed) -> discord.Embed:
        pass
    
    @abstractmethod
    def make_select_option(self, index) -> discord.SelectOption:
        pass

    @abstractmethod
    def add_message(self, message):
        pass

    @abstractmethod
    def kill(self):
        pass

    @abstractmethod
    async def delete_messages(self):
        pass

    @abstractmethod
    def get_edit_window(self) -> discord.ui.Modal:
        pass