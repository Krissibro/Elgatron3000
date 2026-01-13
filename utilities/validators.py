from typing import Optional
import discord

from utilities.helper_functions import parse_time
from utilities.errors import ElgatronError

def validate_interval(interval: str) -> int:
    time = parse_time(interval)
    return time


def validate_natural_number(amount: str) -> int:
    integer: int = validate_digit(amount)
    if integer < 0:
        raise ElgatronError("a valid number.\nAmount must be a whole number higher than 0.")
    return integer


def validate_digit(amount: str) -> int:
    if not amount.isdigit():
        raise ElgatronError(f"{amount} is not a valid number,\nAmount must be a whole number.")
    return int(amount)


def validate_messageable(channel: Optional[discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread]) -> discord.abc.Messageable:
    if not isinstance(channel, discord.abc.Messageable):
        raise ElgatronError("The specified channel is not a text channel.")
    return channel