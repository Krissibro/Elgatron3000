from typing import Optional
import discord

from utilities.helper_functions import parse_time

def validate_interval(interval: str) -> int | discord.Embed:
    try:
        time = parse_time(interval)
        return time
    except ValueError:
        return discord.Embed(title=f"{interval} is not a valid interval.\nInput must be formatted as _d_h_m_s, i.e. 10m10s.")


def validate_natural_number(amount: str) -> int | discord.Embed:
    integer: int | discord.Embed = validate_digit(amount)
    if isinstance(integer, discord.Embed):
        return integer
    elif integer < 0:
        return discord.Embed(title=f"{amount} is not a valid number.\nAmount must be a whole number higher than 0.")
    return integer


def validate_digit(amount: str) -> int | discord.Embed:
    if not amount.isdigit():
        return discord.Embed(title=f"{amount} is not a valid number,\nAmount must be a whole number.")
    return int(amount)


def validate_messageable(channel: Optional[discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread]) -> discord.abc.Messageable | discord.Embed:
    if not isinstance(channel, discord.abc.Messageable):
        return discord.Embed(title="The specified channel is not a text channel.")
    return channel