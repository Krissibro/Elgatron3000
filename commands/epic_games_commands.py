import discord

from epicstore_api import EpicGamesStoreAPI
from apscheduler.triggers.cron import CronTrigger

from utilities.settings import testing, game_channel_id, testing_channel_id
from utilities.settings import guild_id, bot, scheduler, tree
from utilities.state_helper import save_state, load_state
from typing import List, Dict




async def make_link_embed():
    embed = discord.Embed(title="Free Games INCOMING!!!!")
    embed.description = ("[**Epic Games**](https://store.epicgames.com/en-US/free-games)\n" +
                         "[**Playstation Games**](https://www.playstation.com/en-us/ps-plus/whats-new/#monthly-games)")
    return embed


async def get_free_games() -> List[dict]:
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


async def send_games_embed(channel: discord.TextChannel, games: List[dict]) -> None:
    """
    :param channel: The channel you want to send the Games Embed to
    :param games: Dictionary with game data.
    :return:
    """
    for game in games:
        try:
            # page_slug = game["catalogNs"]["mappings"][0]["pageSlug"]
            page_slug = game["productSlug"]
            url = f"\n[**Link**](https://store.epicgames.com/en-US/p/{page_slug})" if page_slug else ""
        except IndexError:
            url = ""

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
async def free_games_rn(ctx: discord.Interaction):
    await ctx.response.send_message(embed=await make_link_embed())
    free_games = await get_free_games()
    await send_games_embed(ctx.channel, free_games)


def get_free_games_state() -> List[dict]:
    state = load_state()
    return state["free_games"]


def update_free_games_state(free_games: List[dict]) -> None:
    state = load_state()
    state["free_games"] = free_games
    save_state(state)


previous_free_game_titles = get_free_games_state()


async def scheduled_post_free_games() -> None:
    global previous_free_game_titles
    free_games = await get_free_games()
    current_free_game_titles = [game["title"] for game in free_games]

    if current_free_game_titles != previous_free_game_titles and free_games:
        # Update the state
        previous_free_game_titles = current_free_game_titles
        update_free_games_state(current_free_game_titles)

        if not testing:
            channel = bot.get_channel(game_channel_id)
        else:
            channel = bot.get_channel(testing_channel_id)

        # Send the free games embed
        await channel.send(embed=await make_link_embed())
        await send_games_embed(channel, free_games)


async def schedule_post_free_games() -> None:
    trigger = CronTrigger(hour=18, minute=0, second=0, timezone='Europe/Oslo')
    job_id = "post_free_games"
    if not scheduler.get_job(job_id):
        scheduler.add_job(scheduled_post_free_games, trigger, id=job_id)
        scheduler.start()
        scheduler.print_jobs()

