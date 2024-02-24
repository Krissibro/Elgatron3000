from utilities.shared import *
from utilities.settings import guild_id
import random

pins = []


async def initialize_guess_that_pin():
    guild = client.get_guild(guild_id)
    # only fetch pins from the bruh channel
    channel_pins = await guild.text_channels[4].pins()
    pins.extend(channel_pins)

    # Fetch pins from all channels
    # for channel in guild.text_channels:
    #     print(f"Fetching pins from {channel.name}")
    #     try:
    #         channel_pins = await channel.pins()
    #         print(f"Fetched {len(channel_pins)} pins")
    #         pins.extend(channel_pins)
    #     except Exception as e:
    #         print(f"Failed to fetch pins from {channel.name}: {e}")
    #
    # print(f"Initialized with {len(pins)} pins")


@tree.command(
    name="guess_that_pin",
    description="Guess the pin!",
    guild=discord.Object(id=guild_id)
)
async def guess_that_pin(ctx):
    if not pins:
        await ctx.response.send_message("No pinned messages found.")
        return

    pin = random.choice(pins)

    for member in client.get_guild(guild_id).members:
        print(member.display_name, len(member.display_name))

    # Pad the username to make it hard to see who made the pin
    max_username_length = max(len(user.display_name) for user in client.get_guild(guild_id).members)
    pin_author = pin.author.display_name + "\u00A0" * (max_username_length - len(pin.author.display_name))

    embed = discord.Embed(title="Guess the pin!",
                          description=pin.content if pin.content else "No text :thinking:")
    embed.add_field(name="By",
                    value=f"||{pin_author}||", inline=True)
    embed.add_field(name="Context",
                    value=f"https://discord.com/channels/{guild_id}/{pin.channel.id}/{pin.id}")

    await ctx.response.send_message(embed=embed)

    if pin.attachments:
        await ctx.channel.send("\n".join(attachment.url for attachment in pin.attachments))


