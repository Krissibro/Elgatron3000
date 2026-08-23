import random
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
import numpy as np
from tortoise import BaseDBAsyncClient

from app.models.wordle import WordleGame, WordleGuess, WordleStats
from app.utilities.decorators import transaction
from app.utilities.errors import ElgatronError


class WordleDB:
    def __init__(self, word_path: Path, testing: bool = False):
        self.testing: bool = testing

        self.valid_words: set[str] = set(
            np.genfromtxt(
                word_path / "valid-words.csv", delimiter=",", dtype=str
            ).flatten()
        )  # all words
        word_bank: set[str] = set(
            np.genfromtxt(
                word_path / "word-bank.csv", delimiter=",", dtype=str
            ).flatten()
        )  # words that can be chosen
        whitelisted_words: set[str] = set(
            np.genfromtxt(
                word_path / "whitelisted-words.csv", delimiter=",", dtype=str
            ).flatten()
        )  # custom words

        self.word_bank: list[str] = list(word_bank | whitelisted_words)
        self.valid_words |= whitelisted_words

    @transaction
    async def new_game(
        self, guild_id: int, connection: BaseDBAsyncClient | None = None
    ) -> WordleGame:
        random_word = random.choice(self.word_bank).upper()
        game = await WordleGame.create(
            guild_id=guild_id,
            word=random_word,
            game_date=datetime.now(tz=ZoneInfo("Europe/Oslo")).date(),
            using_db=connection,
        )

        await game.fetch_related("guesses", using_db=connection)
        return game

    @transaction
    async def guess_word(
        self,
        server_id: int,
        guessed_word: str,
        user: discord.User | discord.Member,
        connection: BaseDBAsyncClient | None = None,
    ) -> None:
        game = await self.get_current_game(guild_id=server_id, connection=connection)

        guessed_word = guessed_word.strip().upper()
        self.validate_wordle_guess(guessed_word, user, game)

        await WordleGuess.create(
            guesser_id=user.id,
            guesser_name=user.display_name,
            word=guessed_word,
            time=datetime.now(tz=ZoneInfo("Europe/Oslo")),
            game=game,
            using_db=connection,
        )

    @transaction
    async def handle_win(
        self,
        server_id: int,
        game: WordleGame,
        connection: BaseDBAsyncClient | None = None,
    ) -> None:
        stats = await self.get_wordle_stats(server_id, connection=connection)

        if (time_taken := game.time_taken()) is None:
            time_taken = timedelta(hours=23, minutes=59, seconds=59)
        guess_count = game.guess_count()

        stats.total_games += 1
        stats.total_guesses += guess_count
        stats.win_streak += 1
        stats.longest_win_streak = max(stats.longest_win_streak, stats.win_streak)
        stats.total_wins += 1
        stats.fastest_win = min(stats.fastest_win, time_taken)
        stats.guess_distribution[guess_count] = (
            stats.guess_distribution.get(guess_count, 0) + 1
        )

        await stats.save(using_db=connection)

    @transaction
    async def handle_loss(
        self,
        server_id: int,
        game: WordleGame,
        connection: BaseDBAsyncClient | None = None,
    ) -> None:
        stats = await self.get_wordle_stats(server_id, connection=connection)

        stats.total_games += 1
        stats.win_streak = 0
        await stats.save(using_db=connection)

    @transaction
    async def recalculate_stats(
        self, server_id: int, connection: BaseDBAsyncClient | None = None
    ) -> None:
        stats = await self.get_wordle_stats(server_id, connection=connection)
        games = (
            await WordleGame.filter(guild_id=server_id)
            .prefetch_related("guesses")
            .using_db(connection)
        )
        current_game_id = max((game.id for game in games), default=None)

        stats.total_games = 0
        stats.total_wins = 0
        stats.total_guesses = 0
        stats.win_streak = 0
        stats.longest_win_streak = 0
        stats.fastest_win = timedelta(hours=23, minutes=59, seconds=59)
        stats.guess_distribution = {}
        await stats.save(using_db=connection)

        # Replay completed games in chronological order. The latest unfinished
        # game is still active and should not count as a loss yet.
        for game in sorted(games, key=lambda g: g.game_date or date.min):
            if game.is_finished():
                await self.handle_win(server_id, game, connection=connection)
            elif game.id != current_game_id:
                await self.handle_loss(server_id, game, connection=connection)

    @transaction
    async def get_current_game(
        self, guild_id: int, connection: BaseDBAsyncClient | None = None
    ) -> WordleGame:
        game = (
            await WordleGame.filter(guild_id=guild_id)
            .using_db(connection)
            .prefetch_related("guesses")
            .last()
        )
        # if no game exists, create a new one
        if game is None:
            game = await self.new_game(guild_id=guild_id, connection=connection)
        return game

    @transaction
    async def get_wordle_stats(
        self, server_id: int, connection: BaseDBAsyncClient | None = None
    ) -> WordleStats:
        stats, _ = await WordleStats.get_or_create(
            server_id=server_id, using_db=connection
        )
        return stats

    def validate_wordle_guess(
        self, guess: str, user: discord.User | discord.Member, game: WordleGame
    ) -> None:
        """
        raises error if guessed word is invalid
        :param guess: the guessed word.
        :param game: the game object.
        """
        existing_ids = {g.guesser_id for g in game.guesses}
        existing_words = {g.word for g in game.guesses}

        if game.word in existing_words:
            raise ElgatronError("The daily wordle has already been solved!")

        if not self.testing:
            if user.id in existing_ids:
                raise ElgatronError(f"{user.display_name} has already guessed.")
            if len(guess) != 5:
                raise ElgatronError("The word must be 5 letters long.")
            if guess not in self.valid_words:
                raise ElgatronError(f'"{guess}" is not a valid word.')
        if len(guess) > 16:  # error can only occur in testing mode
            raise ElgatronError("The guessed word is too long.")
        if guess in existing_words:
            raise ElgatronError(f'"{guess}" has already been guessed.')
