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


if __name__ == "__main__":
    print(parse_time("1d2h5m56s"))
    print(format_seconds(parse_time("1d2h5m56s")))
