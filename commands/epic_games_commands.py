from epicstore_api import EpicGamesStoreAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from utilities.shared import *


async def post_free_games(channel):
    api = EpicGamesStoreAPI()
    free_games = api.get_free_games()["data"]["Catalog"]["searchStore"]["elements"]

    epic_games_embed = discord.Embed(title="Free Epic Games!!!",
                                     description="https://store.epicgames.com/en-US/free-games")
    await channel.send(embed=epic_games_embed)

    playstation_embed = discord.Embed(title="Free Piss Games!!!",
                                      description="https://www.playstation.com/en-us/ps-plus/whats-new/#monthly-games")
    await channel.send(embed=playstation_embed)

    for game in free_games:
        # Check if there is a promotion
        if game["promotions"] and game["promotions"]["promotionalOffers"]:

            # What the fuck is this nested garbage lmao
            promotions = game["promotions"]["promotionalOffers"][0]["promotionalOffers"]

            # Check that the current promotion is 0%
            for promotion in promotions:
                if promotion["discountSetting"]["discountPercentage"] == 0:
                    embed = discord.Embed(title=game["title"], description=game["description"])

                    for image in game["keyImages"]:
                        if image["type"] == "Thumbnail":
                            embed.set_image(url=image["url"])

                    await channel.send(embed=embed)


@tree.command(
    name="free_games_rn",
    description="See the currently free games on Epic Games",
    guild=discord.Object(id=guild_id)
)
async def free_games_rn(ctx):
    await ctx.response.send_message(embed=discord.Embed(title="Free Games INCOMING!!!!"))
    await post_free_games(ctx.channel)


async def scheduled_command():
    channel = client.get_channel(1111353625638350893)

    await channel.send(embed=discord.Embed(title="Free Games INCOMING!!!!"))
    await post_free_games(channel)


async def schedule_post_free_games():
    scheduler = AsyncIOScheduler(timezone='Europe/Oslo')
    trigger = CronTrigger(day_of_week='fri', hour=18, minute=0, second=0, timezone='Europe/Oslo')
    scheduler.add_job(scheduled_command, trigger)
    scheduler.start()

    scheduler.print_jobs()
