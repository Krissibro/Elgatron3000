from abc import ABC, abstractmethod
from utilities.shared import *


class CommandInfo(ABC):
    @abstractmethod
    def __init__(self, channel: discord.TextChannel):
        self.channel = channel
        self.messages = []

    @abstractmethod
    def make_embed(self) -> discord.Embed:
        pass

    def make_overview(self, index, embed) -> discord.Embed:
        pass

    def make_select_option(self, index) -> discord.Embed:
        pass

    def add_message(self, message):
        self.messages.append(message)

    async def delete_messages(self):
        await self.channel.delete_messages(self.messages[1:])
        # Old solution
        # await asyncio.gather(*[i.delete() for i in current_command.info.messages])

    # async def delete_messages_except_first(self):
    #     await self.channel.delete_messages(self.messages[1:])

    # TODO: find a good place for this, i think it could be used elsewhere, so who knows where we should put it
    @classmethod
    def id_to_emoji(cls, command_id: int) -> str:
        emoji_dict = {"0": ":zero:",
                      "1": ":one:",
                      "2": ":two:",
                      "3": ":three:",
                      "4": ":four:",
                      "5": ":five:",
                      "6": ":six:",
                      "7": ":seven:",
                      "8": ":eight:",
                      "9": ":nine:"}
        temp = ""
        for i in str(command_id):
            temp += emoji_dict[i]
        return temp
