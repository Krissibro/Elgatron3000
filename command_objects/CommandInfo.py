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

    def add_message(self, message):
        self.messages.append(message)

    async def delete_messages(self):
        await self.channel.delete_messages(self.messages[1:])
        # await asyncio.gather(*[i.delete() for i in current_command.info.messages])

    # async def delete_messages_except_first(self):
    #     await self.channel.delete_messages(self.messages[1:])
