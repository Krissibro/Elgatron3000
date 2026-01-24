import string

import numpy as np
import random
import discord

from datetime import datetime
from typing import Iterable, Union, List, Set, Optional

from app.core.elgatron import Elgatron
from app.models.wordle_model import WordleGuess, WordleGame
from app.utilities.errors import ElgatronError


class WordleModelDB:
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot

        self.current_game: Optional[WordleGame] = None
        self.correct_guess: bool = False

        self.known_letters: Set[str] = set()
        self.unknown_letters: Set[str] = set(string.ascii_uppercase)

        self.valid_words = set(np.genfromtxt('./static/word_lists/valid-words.csv', delimiter=',', dtype=str).flatten()) # all words
        self.word_bank = set(np.genfromtxt('./static/word_lists/word-bank.csv', delimiter=',', dtype=str).flatten()) # words that can be chosen
        whitelisted_words = set(np.genfromtxt('./static/word_lists/whitelisted-words.csv', delimiter=',', dtype=str).flatten()) # custom words

        self.valid_words |= whitelisted_words
        self.word_bank |= whitelisted_words

    async def new_game(self) -> None:
        self.known_letters: Set[str] = set()
        self.unknown_letters: Set[str] = set(string.ascii_uppercase)
        self.correct_guess: bool = False

        random_word = str(random.choice(tuple(self.word_bank)))
        date = datetime.today()

        self.current_game = await WordleGame.create(
            word=random_word.upper(),
            date=date
        )

    async def guess_word(self, guessed_word: str, user: Union[discord.User, discord.Member]) -> List[int]:
        if self.current_game is None:
            raise ElgatronError("The game has not yet been created")

        guess = WordleGuess(
            guesser_id =user.id,
            guesser_name=user.display_name,
            word=guessed_word.strip().upper(),
            time=datetime.now(),
            game=self.current_game
        )
        await self.current_game.fetch_related("guesses")
        guesses = self.current_game.guesses
        await self.check_valid_guess(guess, guesses)

        await guess.save()
        await guess.fetch_related("game")

        if self.current_game.first_guess_time is None:
            self.current_game.first_guess_time = guess.time

        if guess.word == self.current_game.word:
            self.correct_guess = True
            self.current_game.final_guess_time = guess.time

        result = self.wordle_logic(guess.word, self.current_game.word)
        self.update_letters(guess.word, result)

        return result

    def update_letters(self, word, result) -> None:
        for letter, score in zip(word, result):
            self.unknown_letters.discard(letter)
            if score != 0:
                self.known_letters.add(letter)

    def wordle_logic(self, guess: str, daily_word: str) -> List[int]:
        """
        Function to handle wordle logic
        :return: String of 0, 1, and 2 corresponding to red, yellow and green.
        :
        """
        assert self.current_game is not None
        answer: str = daily_word.upper()

        # Initialize the result with all red squares
        guess_result: List[int] = [0] * len(guess)
        yellow_checker: List[str | None] = list(answer)

        # Check for correct letters (green)
        for i, letter in enumerate(guess):
            if i < len(answer) and letter == answer[i]:
                guess_result[i] = 2
                yellow_checker[i] = None  # mark as used

        # Check for letters in the word but in the wrong place (yellow)
        for i, letter in enumerate(guess):
            if guess_result[i] == 0 and letter in yellow_checker:
                guess_result[i] = 1
                yellow_checker[yellow_checker.index(letter)] = None  # mark as used

        return guess_result

    async def check_valid_guess(self, guess: WordleGuess, guesses: Iterable[WordleGuess]) -> None:
        """
        raises error if guessed word is invalid
        :param guess: the guessed word.
        :param guesses: list of previously guessed words.
        """
        if self.correct_guess:
            raise ElgatronError("The daily wordle has already been guessed")

        existing_ids = {g.guesser_id for g in guesses}
        existing_words = {g.word for g in guesses}

        if not self.bot.testing:
            if guess.guesser_id in existing_ids:
                raise ElgatronError(f"{guess.guesser_name} has already guessed")
            if guess.word not in self.valid_words:
                if len(guess.word) != 5:
                    raise ElgatronError("The word must be 5 letters long")

                raise ElgatronError(f'"{guess.word}" is not a valid word')
        if guess.word in existing_words:
            raise ElgatronError(f'"{guess.word}" has already been guessed')
        if len(guess.word) > 255:
            raise ElgatronError("The word must be 255 characters or less")

    async def setup(self):
        await self.load_game()

    async def load_game(self) -> None:
        today = datetime.today().date()
        self.current_game = (
            await WordleGame
            .filter(date__date=today)
            .prefetch_related("guesses")
            .first()
        )

        if self.current_game is None:
            await self.new_game()
            return

        for g in self.current_game.guesses:
            result = self.wordle_logic(g.word, self.current_game.word)
            self.update_letters(g.word, result)
            self.correct_guess |= g.is_correct()
