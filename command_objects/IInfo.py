from abc import ABC, abstractmethod
from utilities.shared import *


class IInfo(ABC):
    @abstractmethod
    def __init__(self):
        self.messages = []

    @abstractmethod
    def make_embed(self) -> discord.Embed:
        pass
