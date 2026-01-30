from datetime import timedelta


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
    
    return " ".join([emoji_dict[i] for i in str(command_id).lower()])

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
