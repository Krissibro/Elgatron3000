import numpy as np
import random
import discord

from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Optional, Union, Set

from tortoise import BaseDBAsyncClient

from app.models.wordle import WordleGuess, WordleGame, WordleStats
from app.utilities.errors import ElgatronError
from app.utilities.decorators import transaction


class WordleDB:
    def __init__(self, word_path: Path, testing: bool=False):
        self.testing: bool = testing

        self.valid_words: Set[str] = set(np.genfromtxt(word_path / 'valid-words.csv', delimiter=',', dtype=str).flatten()) # all words
        word_bank: Set[str] = set(np.genfromtxt(word_path / 'word-bank.csv', delimiter=',', dtype=str).flatten()) # words that can be chosen
        whitelisted_words: Set[str] = set(np.genfromtxt(word_path / 'whitelisted-words.csv', delimiter=',', dtype=str).flatten()) # custom words

        self.word_bank: List[str] = list(word_bank | whitelisted_words)
        self.valid_words |= whitelisted_words

    @transaction
    async def new_game(self, connection: Optional[BaseDBAsyncClient] = None) -> WordleGame:            
        random_word = random.choice(self.word_bank).upper()
        game =  await WordleGame.create(
            word=random_word,
            game_date=date.today(),
            using_db=connection
        )

        await game.fetch_related("guesses", using_db=connection)
        return game

    @transaction
    async def guess_word(self, guessed_word: str, user: Union[discord.User, discord.Member], connection: Optional[BaseDBAsyncClient] = None) -> None:
        game = await self.get_current_game(connection=connection)
        
        guessed_word = guessed_word.strip().upper()
        self.validate_wordle_guess(guessed_word, user, game)

        await WordleGuess.create(
            guesser_id =user.id,
            guesser_name=user.display_name,
            word=guessed_word,
            time=datetime.now(),
            game=game,
            using_db=connection
        )
    
    @transaction
    async def handle_win(self, server_id: int, game: WordleGame, connection: Optional[BaseDBAsyncClient] = None) -> None:
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
        stats.guess_distribution[guess_count] = stats.guess_distribution.get(guess_count, 0) + 1
        
        await stats.save(using_db=connection)

    @transaction
    async def handle_loss(self, server_id: int, game: WordleGame, connection: Optional[BaseDBAsyncClient] = None) -> None:
        stats = await self.get_wordle_stats(server_id, connection=connection)

        stats.total_games += 1
        stats.win_streak = 0
        await stats.save(using_db=connection)
    
    @transaction
    async def recalculate_stats(self, server_id: int, connection: Optional[BaseDBAsyncClient] = None) -> None:
        stats = await self.get_wordle_stats(server_id, connection=connection)

        games = (
            await WordleGame
            .all()
            .prefetch_related("guesses")
            .using_db(connection)
        )

        # reset stats
        stats.total_games = 0
        stats.total_wins = 0
        stats.total_guesses = 0
        stats.win_streak = 0
        stats.longest_win_streak = 0
        stats.fastest_win = timedelta(hours=23, minutes=59, seconds=59)
        stats.guess_distribution.clear()
        await stats.save(using_db=connection)

        # replay history in order
        for game in sorted(games, key=lambda g: g.game_date or date.min):
            if game.is_finished():
                await self.handle_win(server_id, game, connection=connection)
            else:
                await self.handle_loss(server_id, game, connection=connection)

    @transaction
    async def get_current_game(self, connection: Optional[BaseDBAsyncClient] = None) -> WordleGame:            
        game = (
            await WordleGame
            .filter(game_date=date.today())
            .using_db(connection)
            .prefetch_related("guesses")
            .last()
        )

        if game is None:
            game = await self.new_game(connection=connection)
        return game

    @transaction
    async def get_wordle_stats(self, server_id: int, connection: Optional[BaseDBAsyncClient] = None) -> WordleStats:            
        stats, _ = await WordleStats.get_or_create(server_id=server_id, using_db=connection)
        return stats

    def validate_wordle_guess(self, guess: str, user: Union[discord.User, discord.Member], game: WordleGame) -> None:
        """
        raises error if guessed word is invalid
        :param guess: the guessed word.
        :param game: the game object.
        """
        existing_ids = {g.user_id for g in game.guesses}
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
        if len(guess) > 16: # error can only occur in testing mode
            raise ElgatronError("The guessed word is too long.")
        if guess in existing_words:
            raise ElgatronError(f'"{guess}" has already been guessed.')