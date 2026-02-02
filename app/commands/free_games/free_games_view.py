import discord

from typing import List

from app.commands.free_games.free_games_db import FreeGame

class FreeGamesView:
    async def send_games_embeds(self, current_free_games: List[FreeGame], channel: discord.abc.Messageable) -> None:
        """
        :param channel: The channel you want to send the Games Embed to
        :return:
        """
        for game in current_free_games:
            await channel.send(embed=self.make_game_embed(game))

    def make_game_embed(self, game: FreeGame) -> discord.Embed:
        embed = discord.Embed(title=f"{game.title}",
                              description=f"{game.description} {game.url}")
        embed.set_image(url=game.image_url)
        return embed

    @staticmethod
    def make_link_embed():
        embed = discord.Embed(title="Free Games INCOMING!!!!")
        embed.description = ("[**Epic Games**](https://store.epicgames.com/en-US/free-games)\n" +
                             "[**Playstation Games**](https://www.playstation.com/en-us/ps-plus/whats-new/#monthly-games)")
        return embed