import re

from datetime import timedelta

from utilities.errors import ElgatronError


def parse_time(time_str: str) -> int:
    regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    matchings = regex.match(time_str)
    
    if matchings is not None:
        parts = matchings.groupdict()
    else:
        raise ElgatronError("please enter a valid time format, ex: 1d2h3m4s")

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


def timedelta_format(time_diff: timedelta) -> str:
    """
    Format a timedelta as HH : MM : SS (zero-padded).
    Examples:
      1 s   -> 00 : 00 : 01
      612 s  -> 00 : 01 : 01
      3661 s -> 01 : 01 : 01
    """
    total_seconds = time_diff.seconds
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Zero-pad hours/minutes (2 digits) and seconds_with_ms (width 5, 2 decimals)
    return f"{hours:02} : {minutes:02} : {seconds:02}"
