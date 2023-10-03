import discord
from datetime import datetime, timedelta, time
import asyncio
from epicstore_api import EpicGamesStoreAPI

from utilities.shared import *



@tree.command(
    name="free_games_rn",
    description="See the currently free games on Epic Games",
)
async def free_games_rn(ctx):
    await free_epic(ctx.channel)
    await free_PS(ctx.channel)
    await post_free_games(ctx.channel)


async def free_epic(channel):
    Epic_embed = discord.Embed(title="Free and Epic Games INCOMING!!!!",
                               description="https://store.epicgames.com/en-US/free-games")
    await channel.send(embed=Epic_embed)

async def free_PS(channel):
    PS_embed = discord.Embed(title="Free Pisstation Games INCOMING!!111!!!",
                             description="https://www.playstation.com/en-us/ps-plus/whats-new/#monthly-games")
    await channel.send(embed=PS_embed)

async def post_free_games(channel):
    api = EpicGamesStoreAPI()
    free_games = api.get_free_games()["data"]["Catalog"]["searchStore"]["elements"]

    for game in free_games:
        effective_date = datetime.fromisoformat(game["effectiveDate"][:-1])
        current_datetime = datetime.utcnow()
        seven_days_ago = current_datetime - timedelta(days=7)
        if effective_date < current_datetime and not effective_date < seven_days_ago:
            embed = discord.Embed(title=game["title"], description=game["description"])

            for image in game["keyImages"]:
                if image["type"] == "Thumbnail":
                    embed.set_image(url=image["url"])

            await channel.send(embed=embed)


async def schedule_post_free_games():
    while True:
        now = datetime.utcnow()
        next_friday = now + timedelta((4 - now.weekday()) % 7)  # 4 represents Friday
        next_run = datetime.combine(next_friday.date(), time(18, 0))  # 18:00 UTC
        print(next_run)

        # If it's already past Friday 18:00, schedule for the next Friday
        if now >= next_run:
            next_run += timedelta(weeks=1)

        seconds_until_next_run = (next_run - now).total_seconds()
        print(seconds_until_next_run)
        await asyncio.sleep(seconds_until_next_run)

        channel = client.get_channel(1111353625638350893)
        
        free_epic(channel)
        await post_free_games(channel)