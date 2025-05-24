import discord

from abc import ABC, abstractmethod


class CommandInfo(ABC):
    @abstractmethod
    def __init__(self, channel: discord.TextChannel):
        self.channel = channel

    @abstractmethod
    def make_embed(self) -> discord.Embed:
        pass

    def make_overview(self, index, embed) -> discord.Embed:
        pass

    def make_select_option(self, index) -> discord.Embed:
        pass

    def add_message(self, message):
        pass

    async def delete_messages(self):
        pass
