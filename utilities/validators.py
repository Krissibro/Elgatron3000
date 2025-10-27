from typing import Optional, Union
import discord

from utilities.helper_functions import parse_time

def validate_interval(interval: str) -> int | discord.Embed:
    time: int = parse_time(interval)
    if time <= 0:
        return discord.Embed(title="Input must be formatted as _d_h_m_s, i.e. 10m10s.")
    return time


def validate_natural_number(amount: str) -> int | discord.Embed:
    integer: int | discord.Embed = validate_digit(amount)
    if isinstance(integer, discord.Embed):
        return integer
    elif integer < 0:
        return discord.Embed(title="Amount cannot be less than or equal to 0")
    return integer


def validate_digit(amount: str) -> int | discord.Embed:
    if not amount.isdigit():
        return discord.Embed(title=f"{amount} is not a valid number")
    return int(amount)

def validate_text_channel(channel: Optional[Union[discord.abc.GuildChannel, discord.abc.PrivateChannel, discord.Thread]]) -> Optional[discord.TextChannel]:
    if not isinstance(channel, discord.TextChannel):
        return None
    return channel