import re
from datetime import datetime, timedelta

import discord
from discord import app_commands

from app.utilities.errors import ElgatronError

class IntervalTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> timedelta:
        regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
        matchings = regex.match(value)

        if matchings is not None:
            parts = matchings.groupdict()
        else:
            raise ElgatronError("please enter a valid time format, ex: 1d2h3m4s")

        time_params = {x: int(y) for (x, y) in parts.items() if y}

        if not time_params:
            raise ElgatronError("Invalid interval format. Please use formats like '10s', '5m5s', '2h30m', etc.")

        return timedelta(**time_params)
    
class DateTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> datetime:
        try:
            result = datetime.strptime(value, "%d.%m.%y", )
            return result
        except ValueError:
            pass

        try:
            result = datetime.strptime(value, "%d.%m", )
            result = result.replace(year=datetime.now().year)
            return result
        except ValueError:
            pass

        raise ElgatronError("Invalid date format. Please format as '1.1.21' or '1.1'.")

    
class PositiveIntTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> int:
        int_value = int(value)

        if int_value < 0:
            raise ElgatronError("Value must be positive.")

        return int_value
