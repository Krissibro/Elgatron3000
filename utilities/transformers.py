import discord
from discord import app_commands

from datetime import datetime, timedelta

from utilities.helper_functions import parse_time

class IntervalTranfsormer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> timedelta:

        interval = timedelta(seconds=parse_time(value))
        if interval.seconds == 0: # invalid time format 
            embed = discord.Embed(
                title="Invalid interval format. Please use formats like '10s', '5m5s', '2h30m', etc."
                )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
                )
        return interval
    
class DateTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> datetime:
        # TODO Placeholder implementation, do some error handling
        return datetime.strptime(value, "%Y-%m-%d")
    
class PositiveIntTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> int:
        try:
            int_value = int(value)
            if int_value < 0:
                raise ValueError("Value must be positive.")
            return int_value
        except ValueError:
            embed = discord.Embed(
                title="Invalid number format. Please enter a positive integer."
                )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
                )
            return -1