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

    def make_overview(self, index, embed) -> discord.Embed:
        pass

    def make_select_option(self, index) -> discord.SelectOption:
        pass

    def add_message(self, message):
        pass

    def kill(self):
        pass

    async def delete_messages(self):
        pass

    def get_edit_window(self):
        pass