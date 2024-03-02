from utilities.shared import *
from utilities.settings import guild_id
import random
import pickle
import os
import json
from collections import namedtuple

Pin = namedtuple("Pin", ["author", "content", "attachments", "channel", "id"])

class PinManager:
    def __init__(self):
        self.base_filename = "pins"
        self.chunk_size = 150
        self.pin_count = 0

    async def initialize(self):
        os.makedirs("./pin_storage/", exist_ok=True)

        # pins = []
        # guild = client.get_guild(guild_id)
        # # only fetch pins from the bruh channel
        # channel_pins = await guild.text_channels[4].pins()
        #
        # for pin in channel_pins:
        #     print(pin.author.display_name)

        if not self.count_chunks():
            pins = []
            guild = client.get_guild(guild_id)

            # Fetch pins from all channels
            for i, channel in enumerate(guild.text_channels):
                print(f"|{(i * '#'):<{len(guild.text_channels)}}| {len(pins):<{4}} | {channel.name}", end="\n")
                try:
                    channel_pins = await channel.pins()
                    # TODO: Make display_name better looking, it was good before but now it doesnt work??
                    pins.extend(
                        [Pin(pin.author.display_name, pin.content, [attachment.url for attachment in pin.attachments],
                             pin.channel.id, pin.id) for pin in channel_pins])
                except Exception as e:
                    print(f"Failed to fetch pins from {channel.name}: {e}")

            print(f"Initialized with {len(pins)} pins")

            self.store_pin_count(len(pins))
            self.save_chunks(pins)

            del pins

        else:
            self.read_pin_count()

            print(f"Found {self.count_chunks()} chunks with {self.pin_count} pins")

    def save_chunks(self, data):
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i+self.chunk_size]
            with open(f"./pin_storage/{self.base_filename}_{i // self.chunk_size}.pkl", "wb") as file:
                pickle.dump(chunk, file)

    def count_chunks(self):
        directory = os.listdir("./pin_storage/")
        chunks = [file for file in directory if file.startswith(self.base_filename)]
        return len(chunks)

    def store_pin_count(self, data):
        with open(f"./pin_storage/metadata.json", "w") as file:
            json.dump(data, file)

    def read_pin_count(self):
        with open(f"./pin_storage/metadata.json", "r") as file:
            self.pin_count = json.load(file)

    def load_random_pin(self):
        random_pin_index = random.randint(0, self.pin_count - 1)
        chunk_index = random_pin_index // self.chunk_size
        pin_index_within_chunk = random_pin_index % self.chunk_size

        with open(f"./pin_storage/{self.base_filename}_{chunk_index}.pkl", "rb") as file:
            chunk = pickle.load(file)
            return chunk[pin_index_within_chunk]


pin_manager = PinManager()


async def initialize_guess_that_pin():
    await pin_manager.initialize()


@tree.command(
    name="guess_that_pin",
    description="Guess the pin!",
    guild=discord.Object(id=guild_id)
)
async def guess_that_pin(ctx):
    if not pin_manager.count_chunks():
        await ctx.response.send_message("No pinned messages found.")
        return

    pin = pin_manager.load_random_pin()

    for member in client.get_guild(guild_id).members:
        print(member.display_name, len(member.display_name))

    # Pad the username to make it hard to see who made the pin
    # max_username_length = max(len(user.display_name) for user in client.get_guild(guild_id).members)
    # pin_author = pin.author.display_name + "\u00A0" * (max_username_length - len(pin.author.display_name))

    embed = discord.Embed(title="Guess the pin!",
                          description=pin.content if pin.content else "No text :thinking:")
    embed.add_field(name="By",
                    value=f"||{pin.author}||", inline=True)
    embed.add_field(name="Context",
                    value=f"https://discord.com/channels/{guild_id}/{pin.channel}/{pin.id}")

    await ctx.response.send_message(embed=embed)

    if pin.attachments:
        await ctx.channel.send("\n".join(attachment for attachment in pin.attachments))


