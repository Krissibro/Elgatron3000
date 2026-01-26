import numpy as np
import random
import discord

from datetime import datetime, date
from typing import Union, Optional

from app.models.wordle_model import WordleGuess, WordleGame
from app.utilities.errors import ElgatronError


class WordleDB:
    def __init__(self, testing: bool=False):
        self.testing: bool = testing

        self.valid_words = set(np.genfromtxt('./static/word_lists/valid-words.csv', delimiter=',', dtype=str).flatten()) # all words
        self.word_bank = set(np.genfromtxt('./static/word_lists/word-bank.csv', delimiter=',', dtype=str).flatten()) # words that can be chosen
        whitelisted_words = set(np.genfromtxt('./static/word_lists/whitelisted-words.csv', delimiter=',', dtype=str).flatten()) # custom words

        self.valid_words |= whitelisted_words
        self.word_bank |= whitelisted_words

    async def new_game(self) -> WordleGame:
        random_word = random.choice(tuple(self.word_bank)).upper()
        game =  await WordleGame.create(
            word=random_word,
            game_date=date.today()
        )
        await game.fetch_related("guesses")
        return game

    async def guess_word(self, guessed_word: str, user: Union[discord.User, discord.Member]) -> WordleGame:
        game = await self.get_current_game()

        guess = WordleGuess(
            guesser_id =user.id,
            guesser_name=user.display_name,
            word=guessed_word.strip().upper(),
            time=datetime.now(),
            game=game
        )

        self.validate_wordle_guess(guess, game)
        await guess.save()

        if game.first_guess_time is None:
            game.first_guess_time = guess.time

        if guess.word == game.word:
            game.finished = True
            game.final_guess_time = guess.time

        await game.save()
        return game

    def validate_wordle_guess(self, guess: WordleGuess, game: WordleGame) -> None:
        """
        raises error if guessed word is invalid
        :param guess: the guessed word.
        :param game: the game object.
        """
        existing_ids = {g.guesser_id for g in game.guesses}
        existing_words = {g.word for g in game.guesses}

        if game.finished:
            raise ElgatronError("The daily wordle has already been guessed")

        if not self.testing:
            if guess.guesser_id in existing_ids:
                raise ElgatronError(f"{guess.guesser_name} has already guessed")
            if len(guess.word) != 5:
                raise ElgatronError("The word must be 5 letters long")
            if guess.word not in self.valid_words:
                raise ElgatronError(f'"{guess.word}" is not a valid word')
        if guess.word in existing_words:
            raise ElgatronError(f'"{guess.word}" has already been guessed')

    async def get_current_game(self) -> WordleGame:
        game = (
            await WordleGame
            .filter(game_date=date.today())
            .prefetch_related("guesses")
            .last()
        )

        if game is None:
            game = await self.new_game()
        return game
    
    async def get_previous_game(self, game: WordleGame) -> Optional[WordleGame]:
        previous_game = (
            await WordleGame
            .filter(id__lt < game.id) 
            .prefetch_related("guesses")
            .last()
        ) 

        return previous_game
    