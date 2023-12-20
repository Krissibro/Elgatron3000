import re
from datetime import timedelta


def parse_time(time_str):
    regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    parts = regex.match(time_str).groupdict()

    time_params = {x: int(y) for (x, y) in parts.items() if y}

    return timedelta(**time_params).total_seconds()


if __name__ == "__main__":
    print(parse_time("1d2h5m56s"))
