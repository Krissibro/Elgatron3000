from typing import Optional
import discord
from discord import app_commands

from datetime import datetime, timedelta

from utilities.helper_functions import parse_time

class IntervalTranfsormer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> Optional[timedelta]:

        interval = timedelta(seconds=parse_time(value))
        if interval != 0:
            return interval

        else: # invalid time format
            embed = discord.Embed(
                title="Invalid interval format. Please use formats like '10s', '5m5s', '2h30m', etc."
                )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
                )
            return None
    
class DateTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> Optional[datetime]:
        try:
            result = datetime.strptime(value, "%d.%m.%y", )
            return result
        except ValueError:
            embed = discord.Embed(
                title="Invalid date format. Please enter a valid date (dd.mm.yy)."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return None

    
class PositiveIntTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> Optional[int]:
        try:
            int_value = int(value)
            if int_value < 0:
                raise ValueError("Value must be positive.")
            return int_value
        except ValueError:
            embed = discord.Embed(
                title="Invalid number format. Please enter a positive integer."
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return None

if "__main__" == __name__:
    print(datetime.strptime("1.1.21", "%d.%m.%y"))