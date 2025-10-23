import discord
import re

from datetime import timedelta


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


def format_millisecond_duration(duration_ms: int) -> str:
    """
    Format a duration in total milliseconds as HH : MM : SS (zero-padded).
    Examples:
      1234 ms   -> 00 : 00 : 01
      61234 ms  -> 00 : 01 : 01
      3661234 ms -> 01 : 01 : 01
    """
    hours = duration_ms // 3_600_000
    minutes = (duration_ms % 3_600_000) // 60_000
    seconds = (duration_ms % 60_000) // 1_000
    milliseconds = duration_ms % 1_000

    # Combine seconds and milliseconds into one float
    # Decided to use only seconds for now, but I will leave this here
    seconds_with_ms = seconds + (milliseconds / 1000.0)

    # Zero-pad hours/minutes (2 digits) and seconds_with_ms (width 5, 2 decimals)
    return f"{hours:02} : {minutes:02} : {seconds:02}"


if __name__ == "__main__":
    print(parse_time("1d2h5m56s"))
    print(format_seconds(parse_time("1d2h5m56s")))
