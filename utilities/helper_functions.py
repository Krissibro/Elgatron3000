import re
from datetime import timedelta


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
    emoji_dict = {"0": ":zero:",
                  "1": ":one:",
                  "2": ":two:",
                  "3": ":three:",
                  "4": ":four:",
                  "5": ":five:",
                  "6": ":six:",
                  "7": ":seven:",
                  "8": ":eight:",
                  "9": ":nine:",
                  "a": ":regional_indicator_a:",
                  "b": ":regional_indicator_b:",
                  "c": ":regional_indicator_c:",
                  "d": ":regional_indicator_d:",
                  "e": ":regional_indicator_e:",
                  "f": ":regional_indicator_f:",
                  "g": ":regional_indicator_g:",
                  "h": ":regional_indicator_h:",
                  "i": ":regional_indicator_i:",
                  "j": ":regional_indicator_j:",
                  "k": ":regional_indicator_k:",
                  "l": ":regional_indicator_l:",
                  "m": ":regional_indicator_m:",
                  "n": ":regional_indicator_n:",
                  "o": ":regional_indicator_o:",
                  "p": ":regional_indicator_p:",
                  "q": ":regional_indicator_q:",
                  "r": ":regional_indicator_r:",
                  "s": ":regional_indicator_s:",
                  "t": ":regional_indicator_t:",
                  "u": ":regional_indicator_u:",
                  "v": ":regional_indicator_v:",
                  "w": ":regional_indicator_w:",
                  "x": ":regional_indicator_x:",
                  "y": ":regional_indicator_y:",
                  "z": ":regional_indicator_z:"
                  }
    temp = ""
    print(command_id)
    for i in str(command_id).lower():
        print(str(i))
        temp += emoji_dict[str(i)]
    return temp


if __name__ == "__main__":
    print(parse_time("1d2h5m56s"))
    print(format_seconds(parse_time("1d2h5m56s")))
