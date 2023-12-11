from utilities.shared import *
from command_objects.IInfo import *


class Command:
    current_ids = set()
    running_commands_dict = {}

    def __init__(self, info: IInfo, task):
        self.id = self.assign_id()
        self.info = info
        self.process = task
        self.running_commands_dict[self.id] = self

    # Assigns the lowest ID
    def assign_id(self):
        i = 1
        while i in self.current_ids:
            i += 1
        self.current_ids.add(i)
        return i

    @classmethod
    def get_ids(cls):
        return cls.current_ids

    def get_embed(self):
        embed = self.info.make_embed()
        embed.add_field(name="ID:", value=f"{self.id}", inline=True)
        return embed

    @classmethod
    def get_embed_by_id(cls, command_id):
        return cls.running_commands_dict[command_id].get_embed()

    def end(self):
        self.current_ids.remove(self.id)
        del self.running_commands_dict[self.id]

    def kill(self):
        self.process.cancel()
        Command.current_ids.remove(self.id)
        del self.running_commands_dict[self.id]

    @classmethod
    def kill_all(cls):
        for command in cls.running_commands_dict.values():
            command.kill()

    @classmethod
    def get_command(cls, command_id):
        return cls.running_commands_dict[command_id]

    @classmethod
    def is_empty(cls):
        return not cls.running_commands_dict
