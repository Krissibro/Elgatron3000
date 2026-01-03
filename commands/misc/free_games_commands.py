import json
import discord
from discord import app_commands
from discord.ext import commands

from epicstore_api import EpicGamesStoreAPI
from apscheduler.triggers.cron import CronTrigger

from utilities.elgatron import Elgatron
from utilities.validators import validate_messageable
from typing import List


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


async def send_games_embed(channel: discord.abc.Messageable, games: List[dict]) -> None:
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


def get_free_games_state() -> List[dict]:
    state = load_state()
    return state["free_games"]


def update_free_games_state(free_games: List[dict]) -> None:
    state = load_state()
    state["free_games"] = free_games
    save_state(state)


async def scheduled_post_free_games(bot: Elgatron) -> None:
    global previous_free_game_titles
    free_games = await get_free_games()
    current_free_game_titles = [game["title"] for game in free_games]

    if current_free_game_titles != previous_free_game_titles and free_games:
        # Update the state
        previous_free_game_titles = current_free_game_titles
        update_free_games_state(current_free_game_titles)

        if not bot.testing:
            channel = bot.get_channel(bot.game_channel_id)
        else:
            channel = bot.get_channel(bot.testing_channel_id)

        channel = validate_messageable(channel)
        if isinstance(channel, discord.Embed):
            raise ValueError("The channel ID provided does not correspond to a text channel.")

        # Send the free games embed
        await channel.send(embed=await make_link_embed())
        await send_games_embed(channel, free_games)


def load_state():
    default_state = {
        "free_games": []
    }
    try:
        with open(state_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If there's no file, or it's corrupted, save the default state to a new file
        save_state(default_state)
        return default_state


def save_state(state):
    with open(state_path, 'w') as file:
        json.dump(state, file, indent=4)


# TODO: Clean up everything in this file and move it into a cog
class EpicGames(commands.Cog):
    def __init__(self, bot: Elgatron):
        self.bot = bot
        trigger = CronTrigger(hour=18, minute=0, second=0, timezone='Europe/Oslo')
        job_id = "post_free_games"
        if not bot.scheduler.get_job(job_id):
            bot.scheduler.add_job(scheduled_post_free_games, trigger=trigger, id=job_id, kwargs={"bot": bot}
)

    @app_commands.command(
        name="free_games_rn",
        description="See the currently free games on Epic Games"
    )
    async def free_games_rn(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed=await make_link_embed())
        free_games = await get_free_games()
        
        channel = validate_messageable(ctx.channel)
        if isinstance(channel, discord.Embed):
            await ctx.followup.send(embed=channel)
            return
        
        await send_games_embed(channel, free_games)


state_path = "./data/bot_state.json"
previous_free_game_titles = get_free_games_state()

async def setup(bot: Elgatron):
    await bot.add_cog(EpicGames(bot), guild=discord.Object(id=bot.guild_id))
