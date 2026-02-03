from datetime import datetime, timezone
from typing import List, Optional

from epicstore_api import EpicGamesStoreAPI
from tortoise import BaseDBAsyncClient
from tortoise.transactions import in_transaction

from app.utilities.decorators import transaction
from app.models.free_games import FreeGame


class FreeGameDB:
    def __init__(self):
        self.api = EpicGamesStoreAPI()
    
    async def update_free_games(self) -> List[FreeGame]:
        new_free_games = self.__get_free_games()
        
        # must use transaction after new_free_games cuz it can be slow.
        async with in_transaction() as connection:
            current_free_games = (
                await FreeGame.filter(end_free_date=None)
                .using_db(connection)
                .all()
            )
            
            current_free_titles = [game.title for game in current_free_games]
            new_free_titles = [game["title"] for game in new_free_games]

            for known_free_game in current_free_games:
                if known_free_game.title not in new_free_titles:
                    known_free_game.end_free_date = datetime.now(tz=timezone.utc)
                    await known_free_game.save()

            new_games = []
            for new_free_game in new_free_games:
                if new_free_game["title"] not in current_free_titles:
                    free_game = await FreeGame.create(
                        title=new_free_game["title"][:128], # ensure max length
                        description=new_free_game["description"],
                        url=self.get_game_url(new_free_game),
                        image_url=self.get_game_image_url(new_free_game),
                        using_db=connection
                    )
                    new_games.append(free_game)
        return new_games

    def __get_free_games(self) -> List[dict]:
        new_free_games = []
        free_games = self.api.get_free_games()["data"]["Catalog"]["searchStore"]["elements"]

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
                new_free_games.append(game)

        return new_free_games

    @staticmethod
    @transaction
    async def get_current_free_games(connection: Optional[BaseDBAsyncClient] = None) -> List[FreeGame]:
        return (
            await FreeGame.filter(end_free_date=None)
            .using_db(connection)
            .all()
        )

    @staticmethod
    def get_game_image_url(game: dict) -> str:
        for image in game["keyImages"]:
            if image["type"] in ["OfferImageWide", "DieselStoreFrontWide"]:
                return image["url"]
        return ""

    @staticmethod
    def get_game_url(game: dict) -> str:
        try:
            # page_slug = game["catalogNs"]["mappings"][0]["pageSlug"]
            page_slug = game["productSlug"] or game["catalogNs"]["mappings"][0]["pageSlug"] or game["offerMappings"][0]["pageSlug"]
            return f"\n[**Link**](https://store.epicgames.com/en-US/p/{page_slug})" if page_slug else ""
        except IndexError:
            return ""