import discord
from discord import app_commands

from datetime import datetime, timedelta

from utilities.helper_functions import parse_time

class IntervalTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> timedelta:

        interval = timedelta(seconds=parse_time(value))
        if interval != 0:
            return interval

        else: # invalid time format
            raise ValueError("Invalid interval format. Please use formats like '10s', '5m5s', '2h30m', etc.")
    
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
        except ValueError :
            pass

        raise ValueError("Invalid date format. Please format as '1.1.21' or '1.1'.")

    
class PositiveIntTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> int:
        int_value = int(value)

        if int_value < 0:
            raise ValueError("Value must be positive.")

        return int_value
