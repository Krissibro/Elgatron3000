from utilities.shared import *
from utilities.settings import guild_id
import random
import pickle
import os
import json
from collections import namedtuple

# Pickle will not store the message object itself, so it had to be dumbed down to a namedtuple
Pin = namedtuple("Pin", ["author", "content", "attachments", "channel", "id"])


class PinManager:
    def __init__(self):
        self.base_filename = "pins"
        self.chunk_size = 150
        self.pin_count = 0

    async def initialize(self):
        """Fetches all pinned messages from the guild and stores them in chunks of 150 pins each."""

        os.makedirs("./pin_storage/", exist_ok=True)

        if not self.count_chunks():
            pins = []
            guild = client.get_guild(guild_id)

            # Fetch pins from all channels
            for i, channel in enumerate(guild.text_channels):
                # Loading bar for fun
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
        """Saves the data in chunks of 150 pins each as pickle objects in pin_storage."""

        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i+self.chunk_size]
            with open(f"./pin_storage/{self.base_filename}_{i // self.chunk_size}.pkl", "wb") as file:
                pickle.dump(chunk, file)

    def count_chunks(self):
        """Returns the number of chunks in pin_storage."""

        directory = os.listdir("./pin_storage/")
        chunks = [file for file in directory if file.startswith(self.base_filename)]
        return len(chunks)

    def store_pin_count(self, data):
        """Stores the number of pins in metadata.json."""

        with open(f"./pin_storage/metadata.json", "w") as file:
            json.dump(data, file)

    def read_pin_count(self):
        """Reads the number of pins from metadata.json."""

        with open(f"./pin_storage/metadata.json", "r") as file:
            self.pin_count = json.load(file)

    def load_random_pin(self):
        """Loads a random pin from the stored chunks."""

        random_pin_index = random.randint(0, self.pin_count - 1)
        chunk_index = random_pin_index // self.chunk_size
        pin_index_within_chunk = random_pin_index % self.chunk_size

        with open(f"./pin_storage/{self.base_filename}_{chunk_index}.pkl", "rb") as file:
            chunk = pickle.load(file)
            return chunk[pin_index_within_chunk]


pin_manager = PinManager()


async def initialize_guess_that_pin():
    await pin_manager.initialize()


class PinView(discord.ui.View):
    def __init__(self, message_ctx, pin):
        super().__init__()
        self.pin = pin
        self.message_ctx = message_ctx
        self.sent_attachments = False

    async def make_first_embed(self):
        """Creates the first embed for the game."""

        embed = discord.Embed(title="Guess the pin!",
                              description=self.pin.content if self.pin.content else None)

        if not self.sent_attachments and self.pin.attachments:
            await self.message_ctx.channel.send("\n".join(attachment for attachment in self.pin.attachments))
            self.sent_attachments = True

        return embed

    @discord.ui.button(label="Reveal the sinner!", style=discord.ButtonStyle.success)
    async def reveal_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Reveals the author of the pinned message and removes the view from the message."""

        embed = await self.make_first_embed()

        embed.add_field(name="By",
                        value=f"**@{self.pin.author}**", inline=True)
        embed.add_field(name="Context",
                        value=f"https://discord.com/channels/{guild_id}/{self.pin.channel}/{self.pin.id}")

        await self.message_ctx.edit_original_response(embed=embed, view=None)
        # self.stop()


@tree.command(
    name="guess_the_pin",
    description="Guess the pin!",
    guild=discord.Object(id=guild_id)
)
async def guess_that_pin(ctx):
    if not pin_manager.count_chunks():
        await ctx.response.send_message("No pinned messages found.")
        return

    pin = pin_manager.load_random_pin()

    view = PinView(ctx, pin)
    embed = await view.make_first_embed()

    await ctx.response.send_message(embed=embed, view=view)


