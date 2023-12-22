import re
from datetime import timedelta


def parse_time(time_str: str) -> int:
    regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    parts = regex.match(time_str).groupdict()

    time_params = {x: int(y) for (x, y) in parts.items() if y}

    return int(timedelta(**time_params).total_seconds())


def format_seconds(seconds: int) -> str:
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_time = ""
    if days:
        formatted_time += f"{days}d"
    if hours:
        formatted_time += f"{hours}h"
    if minutes:
        formatted_time += f"{minutes}m"
    if seconds:
        formatted_time += f"{seconds}s"

    return formatted_time if formatted_time else "0s"


if __name__ == "__main__":
    print(parse_time("1d2h5m56s"))
    print(format_seconds(parse_time("1d2h5m56s")))
