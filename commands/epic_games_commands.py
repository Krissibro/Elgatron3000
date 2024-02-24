from epicstore_api import EpicGamesStoreAPI
from utilities.settings import testing, game_channel_id, testing_channel_id
from utilities.shared import *


previous_free_games = []


async def make_link_embed():
    embed = discord.Embed(title="Free Games INCOMING!!!!")
    embed.description = (f"[**Epic Games**](https://store.epicgames.com/en-US/free-games)\n" +
                         f"[**Playstation Games**](https://www.playstation.com/en-us/ps-plus/whats-new/#monthly-games)")
    return embed


async def get_free_games():
    api = EpicGamesStoreAPI()
    free_games = api.get_free_games()["data"]["Catalog"]["searchStore"]["elements"]

    free_promotions = []

    for game in free_games:
        # Check if there is a promotion
        if not (game["promotions"] and game["promotions"]["promotionalOffers"]):
            continue

        # Accessing the nested promotional offers
        nested_promotions = game["promotions"]["promotionalOffers"][0]["promotionalOffers"]

        for promotion in nested_promotions:
            # Check that the current promotion is 0%
            if promotion["discountSetting"]["discountPercentage"] == 0:
                free_promotions.append(game)
                break  # Assuming only one free promotion per game
    return free_promotions


async def make_game_embeds(channel, games):
    for game in games:
        page_slug = game["catalogNs"]["mappings"][0]["pageSlug"]
        url = f"\n[**Link**](https://store.epicgames.com/en-US/p/{page_slug})" if page_slug else ""

        embed = discord.Embed(title=f"{game['title']}",
                              description=f"{game['description']}" + url)
        for image in game["keyImages"]:
            if image["type"] in ["OfferImageWide", "DieselStoreFrontWide"]:
                embed.set_image(url=image["url"])

        await channel.send(embed=embed)


@tree.command(
    name="free_games_rn",
    description="See the currently free games on Epic Games",
    guild=discord.Object(id=guild_id)
)
async def free_games_rn(ctx):
    await ctx.response.send_message(embed=await make_link_embed())
    free_games = await get_free_games()
    await make_game_embeds(ctx.channel, free_games)


async def scheduled_post_free_games():
    global previous_free_games
    free_games = await get_free_games()
    game_titles = [game["title"] for game in free_games]

    if game_titles == previous_free_games or not free_games:
        return
    previous_free_games = game_titles
    if not testing:
        channel = client.get_channel(game_channel_id)       # Gaming channel
    else:
        channel = client.get_channel(testing_channel_id)      # Test channel

    await channel.send(embed=await make_link_embed())
    await make_game_embeds(channel, free_games)


async def schedule_post_free_games():
    trigger = CronTrigger(hour=18, minute=0, second=0, timezone='Europe/Oslo')
    scheduler.add_job(scheduled_post_free_games, trigger)
    scheduler.start()

