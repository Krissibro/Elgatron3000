from epicstore_api import EpicGamesStoreAPI

from utilities.shared import *


async def make_link_embed():
    embed = discord.Embed(title="Free Games INCOMING!!!!")
    embed.description = (f"[Epic Games](https://store.epicgames.com/en-US/free-games)\n" +
                         f"[Playstation Games](https://www.playstation.com/en-us/ps-plus/whats-new/#monthly-games)")
    return embed


async def post_free_epic_games(channel):
    api = EpicGamesStoreAPI()
    free_games = api.get_free_games()["data"]["Catalog"]["searchStore"]["elements"]

    for game in free_games:
        # Check if there is a promotion
        if not (game["promotions"] and game["promotions"]["promotionalOffers"]):
            continue

        # What the fuck is this nested garbage lmao
        promotions = game["promotions"]["promotionalOffers"][0]["promotionalOffers"]

        for promotion in promotions:
            # Check that the current promotion is 0%
            if promotion["discountSetting"]["discountPercentage"] != 0:
                continue

            embed = discord.Embed(title=game["title"], description=game["description"])

            for image in game["keyImages"]:
                if image["type"] == "OfferImageWide":
                    embed.set_image(url=image["url"])

            await channel.send(embed=embed)


@tree.command(
    name="free_games_rn",
    description="See the currently free games on Epic Games",
    guild=discord.Object(id=guild_id)
)
async def free_games_rn(ctx):
    await ctx.response.send_message(embed=await make_link_embed())
    await post_free_epic_games(ctx.channel)


async def scheduled_post_free_games():
    # Gammin
    channel = client.get_channel(1111353625638350893)
    await channel.send(embed=await make_link_embed())
    await post_free_epic_games(channel)


async def schedule_post_free_games():
    trigger = CronTrigger(day_of_week='thu', hour=18, minute=0, second=0, timezone='Europe/Oslo')
    scheduler.add_job(scheduled_post_free_games, trigger)
    scheduler.start()

