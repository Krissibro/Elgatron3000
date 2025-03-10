import discord
import re

from datetime import timedelta


async def validate_interval(ctx, interval):
    if interval <= 0:
        await ctx.response.send_message(embed=discord.Embed(title="Input must be formatted as _d_h_m_s, i.e. 10m10s."),
                                        ephemeral=True)
        return False
    return True


async def validate_amount(ctx, amount: int):
    if amount <= 0:
        await ctx.response.send_message(embed=discord.Embed(title="Amount cannot be less than or equal to 0"),
                                        ephemeral=True)
        return False
    return True


async def validate_numeric(ctx, amount: str, error_msg: str):
    if not amount.isnumeric():
        await ctx.response.send_message(embed=discord.Embed(title=error_msg), ephemeral=True)
        return False
    return True


def parse_time(time_str: str) -> int:
    regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    parts = regex.match(time_str).groupdict()

    time_params = {x: int(y) for (x, y) in parts.items() if y}

    return int(timedelta(**time_params).total_seconds())


def format_seconds(seconds: int) -> str:
    formatted_time = ""
    for unit, divisor in [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]:
        value, seconds = divmod(seconds, divisor)
        if value:
            formatted_time += f"{value}{unit}"

    return formatted_time if formatted_time else "0s"


def char_to_emoji(command_id) -> str:
    emoji_dict = {"0": "0️⃣",
                  "1": "1️⃣",
                  "2": "2️⃣",
                  "3": "3️⃣",
                  "4": "4️⃣",
                  "5": "5️⃣",
                  "6": "6️⃣",
                  "7": "7️⃣",
                  "8": "8️⃣",
                  "9": "9️⃣",
                  "a": "🇦",
                  "b": "🇧",
                  "c": "🇨",
                  "d": "🇩",
                  "e": "🇪",
                  "f": "🇫",
                  "g": "🇬",
                  "h": "🇭",
                  "i": "🇮",
                  "j": "🇯",
                  "k": "🇰",
                  "l": "🇱",
                  "m": "🇲",
                  "n": "🇳",
                  "o": "🇴",
                  "p": "🇵",
                  "q": "🇶",
                  "r": "🇷",
                  "s": "🇸",
                  "t": "🇹",
                  "u": "🇺",
                  "v": "🇻",
                  "w": "🇼",
                  "x": "🇽",
                  "y": "🇾",
                  "z": "🇿"
                  }
    temp = ""
    for i in str(command_id).lower():
        temp += emoji_dict[str(i)]
    return temp


def format_duration_in_milliseconds(duration_ms: int) -> str:
    """
    Format a duration given in total milliseconds into a string with hours, minutes, and seconds with milliseconds.
    Example output: "6.12 sec"
    """
    hours = duration_ms // 3_600_000
    minutes = (duration_ms % 3_600_000) // 60_000
    seconds = (duration_ms % 60_000) // 1_000
    milliseconds = duration_ms % 1_000

    # Combine seconds and milliseconds into a float
    seconds_with_ms = seconds + (milliseconds / 1000)

    parts = []
    if hours > 0:
        parts.append(f"{hours} hr")
    if hours > 0 or minutes > 0:
        parts.append(f"{minutes} min")

    # Format seconds with 2 decimal places
    parts.append(f"{seconds_with_ms:.2f} sec")

    return " ".join(parts)


if __name__ == "__main__":
    print(parse_time("1d2h5m56s"))
    print(format_seconds(parse_time("1d2h5m56s")))
