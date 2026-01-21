from typing import Optional
import discord

from utilities.errors import ElgatronError

def validate_natural_number(digit: str) -> int:
    integer: int = validate_digit(digit)
    if integer < 0:
        raise ElgatronError(f"{digit} is not a positive whole number.")
    return integer


def validate_digit(digit: str) -> int:
    if not digit.isdigit():
        raise ElgatronError(f"{digit} is not a valid whole number.")
    return int(digit)


def validate_messageable(channel: Optional[discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread]) -> discord.abc.Messageable:
    if not isinstance(channel, discord.abc.Messageable):
        raise ElgatronError("The specified channel is not a text channel.")
    return channel