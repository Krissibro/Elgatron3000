import json
import os
import discord
from discord.ext import commands

from epicstore_api import EpicGamesStoreAPI

from utilities.elgatron import Elgatron
from utilities.validators import validate_messageable
from typing import List
from dataclasses import dataclass

@dataclass
class FreeGame:
    title: str
    description: str
    url: str
    image_url: str

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(title=f"{self.title}",
                              description=f"{self.description} {self.url}")
        embed.set_image(url=self.image_url)
        return embed

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "imageUrl": self.image_url
        }


class FreeGameManager(commands.Cog):
    def __init__(self, bot: Elgatron):
        self.bot = bot
        self.free_games: List[FreeGame] = []

        self.path = "./data/free_game_state.json"
        self.load_state()

    def update_free_games(self) -> None:
        self.free_games = []

        api = EpicGamesStoreAPI()
        free_games = api.get_free_games()["data"]["Catalog"]["searchStore"]["elements"]

        for game in free_games:
            # Check if there is a promotion
            if not (game["promotions"] and game["promotions"]["promotionalOffers"]):
                continue

            # Accessing the nested promotional offers
            nested_promotions = game["promotions"]["promotionalOffers"][0]["promotionalOffers"]

            for promotion in nested_promotions:
                # Check that the current promotion is 0%
                if promotion["discountSetting"]["discountPercentage"] != 0:
                    continue

                free_game = FreeGame(game["title"], game["description"], self.get_game_url(game), self.get_game_image_url(game))
                self.free_games.append(free_game)

        self.free_games.sort(key=lambda g: g.title)
        self.save_state()

    async def send_games_embed(self, channel: discord.abc.Messageable) -> None:
        """
        :param channel: The channel you want to send the Games Embed to
        :return:
        """
        for game in self.free_games:
            await channel.send(embed=game.get_embed())

    async def scheduled_post_free_games(self) -> None:
        previous_free_games = self.free_games
        self.update_free_games()

        if previous_free_games != self.free_games:
            if not self.bot.testing:
                channel = self.bot.get_channel(self.bot.game_channel_id)
            else:
                channel = self.bot.get_channel(self.bot.testing_channel_id)

            channel = validate_messageable(channel)

            # Send the free games embed
            await channel.send(embed=self.make_link_embed())
            await self.send_games_embed(channel)

    @staticmethod
    def make_link_embed():
        embed = discord.Embed(title="Free Games INCOMING!!!!")
        embed.description = ("[**Epic Games**](https://store.epicgames.com/en-US/free-games)\n" +
                             "[**Playstation Games**](https://www.playstation.com/en-us/ps-plus/whats-new/#monthly-games)")
        return embed

    @staticmethod
    def get_game_image_url(game) -> str:
        for image in game["keyImages"]:
            if image["type"] in ["OfferImageWide", "DieselStoreFrontWide"]:
                return image["url"]
        return ""

    @staticmethod
    def get_game_url(game):
        try:
            # page_slug = game["catalogNs"]["mappings"][0]["pageSlug"]
            page_slug = game["productSlug"]
            return f"\n[**Link**](https://store.epicgames.com/en-US/p/{page_slug})" if page_slug else ""
        except IndexError:
            return ""

    def get_dict_of_data(self) -> dict:
        return {
            "free_games": [free_game.to_dict() for free_game in self.free_games],
        }

    def retrieve_data_from_dict(self, data: dict) -> None:
        free_games = data.get("free_games", [])
        for free_game in free_games:
            self.free_games.append(FreeGame(free_game["title"], free_game["description"], free_game["url"], free_game["imageUrl"]))


    def load_state(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as file:
                games_json = json.load(file)
                self.retrieve_data_from_dict(games_json)
        else:
            self.update_free_games()


    def save_state(self):
        with open(self.path, 'w') as file:
            games_dict = self.get_dict_of_data()
            json.dump(games_dict, file, indent=4)