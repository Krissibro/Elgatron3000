from utilities.shared import *
from utilities.settings import guild_id
import random
import pickle
import os
import json
from collections import namedtuple
from math import sqrt

# Pickle will not store the message object itself, so it had to be dumbed down to a namedtuple
Pin = namedtuple("Pin", ["author", "content", "attachments", "channel", "id"])


class PinManager:
    def __init__(self):
        self.base_filename = "pins"
        self.chunk_size = 100
        self.pin_count = 0

    async def initialize(self):
        """Fetches all pinned messages from the guild and stores them in chunks of 150 pins each."""

        os.makedirs("./data/pin_storage/", exist_ok=True)

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

            self.pin_count = len(pins)
            self.chunk_size = round(sqrt(self.pin_count))
            self.store_count_and_chunk_size(self.pin_count, self.chunk_size)
            self.save_chunks(pins)

            del pins

        else:
            self.read_pin_count()

            print(f"Found {self.count_chunks()} chunks with {self.pin_count} pins")

    def save_chunks(self, data):
        """Saves the data in chunks of 150 pins each as pickle objects in pin_storage."""

        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i+self.chunk_size]
            with open(f"./data/pin_storage/{self.base_filename}_{i // self.chunk_size}.pkl", "wb") as file:
                pickle.dump(chunk, file)

    def count_chunks(self):
        """Returns the number of chunks in pin_storage."""
        directory = os.listdir("./data/pin_storage/")
        chunks = [file for file in directory if file.startswith(self.base_filename)]
        return len(chunks)

    def store_count_and_chunk_size(self, count, chunk_size):
        """Stores the number of pins in metadata.json."""
        with open(f"./data/pin_storage/metadata.json", "w") as file:
            json.dump([count, chunk_size], file)

    def read_pin_count(self):
        """Reads the number of pins from metadata.json."""
        with open(f"./data/pin_storage/metadata.json", "r") as file:
            self.pin_count, self.chunk_size = json.load(file)

    def load_random_pin(self):
        """Loads a random pin from the stored chunks."""
        random_pin_index = random.randint(0, self.pin_count - 1)
        chunk_index = random_pin_index // self.chunk_size
        pin_index_within_chunk = random_pin_index % self.chunk_size

        with open(f"./data/pin_storage/{self.base_filename}_{chunk_index}.pkl", "rb") as file:
            chunk = pickle.load(file)
            return chunk[pin_index_within_chunk]

    def add_pin_to_storage(self, pin):
        """Adds a pin to the storage."""

        # Update the pin count
        self.pin_count += 1
        pin_manager.store_count_and_chunk_size(self.pin_count)

        # Calculate the index of the last chunk
        latest_chunk_index = (pin_manager.pin_count - 1) // pin_manager.chunk_size

        pin = Pin(pin.author.display_name, pin.content, [attachment.url for attachment in pin.attachments], pin.channel.id, pin.id)

        # Open that last chunk
        with open(f"./data/pin_storage/{self.base_filename}_{latest_chunk_index}.pkl", "rb") as file:
            chunk = pickle.load(file)

        # Check if a chunk is at capacity, if so make a new chunk
        if len(chunk) == pin_manager.chunk_size:
            latest_chunk_index += 1
            chunk = [pin]
            write_destination = f"./data/pin_storage/{self.base_filename}_{latest_chunk_index}.pkl"
        else:
            chunk.append(pin)
            write_destination = f"./data/pin_storage/{self.base_filename}_{latest_chunk_index}.pkl"

        # Write to either the last chunk or a new chunk
        with open(write_destination, "wb") as file:
            pickle.dump(chunk, file)

    def remove_pin_from_storage(self, pin):
        """Removes a pin from the storage."""

        # Update the pin count
        self.pin_count -= 1
        pin_manager.store_count_and_chunk_size(self.pin_count)

        # Go through each chunk, newest to oldest, till the pin is found, then remove it and update the file
        for chunk_index in range(self.count_chunks() - 1, 0, -1):
            with open(f"./data/pin_storage/{self.base_filename}_{chunk_index}.pkl", "rb") as file:
                chunk = pickle.load(file)
                for stored_pin in chunk:
                    if stored_pin.id == pin.id:
                        chunk.remove(stored_pin)
                        with open(f"./data/pin_storage/{self.base_filename}_{chunk_index}.pkl", "wb") as file:
                            pickle.dump(chunk, file)
                        return


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
        """Creates the embed containing the title and the selected pin.
        Also appends the attachments if there are any"""

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
                        value=f"{self.pin.author}", inline=True)
        embed.add_field(name="Context",
                        value=f"https://discord.com/channels/{guild_id}/{self.pin.channel}/{self.pin.id}")

        await self.message_ctx.edit_original_response(embed=embed, view=None)


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


@client.event
async def on_message_edit(before, after):
    """Detects if a message has been edited.
    If a message is pinned, it is saved to the storage.
    If a message is unpinned, it is removed from storage"""

    # If pinned
    if not before.pinned and after.pinned:
        pin_manager.add_pin_to_storage(after)
        # print(f"Message {after.id} in channel {after.channel.id} was pinned.")

    # If unpinned
    if before.pinned and not after.pinned:
        pin_manager.remove_pin_from_storage(after)
        # print(f"Message {after.id} in channel {after.channel.id} was unpinned.")

    # print(pin_manager.pin_count)
    # with open("./data/pin_storage/pins_8.pkl", "rb") as file:
    #     print(pickle.load(file))

# Todo: handle if a pinned message is deleted or ehhhhhh?


# Alternative method, but without the previous state of the message
# @client.event
# async def on_raw_message_edit(payload):
#     """Detects if any message has been edited.
#     If a message is pinned or have been pinned previously and just edited, it is detected."""
#     print(f"Edit detected")
#     if not client.get_channel(payload.channel_id):
#         return
#     if payload.data["pinned"]:
#         print("Get pinned bitch")






