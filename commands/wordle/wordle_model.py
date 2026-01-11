import json
import os
import random
import string
import numpy as np
import discord

from datetime import datetime
from typing import List, Optional, Set, Union

from commands.wordle.wordle_stats import WordleStats
from utilities.helper_functions import timedelta_format

class WordleModel:
    def __init__(self, wordle_stats: WordleStats, testing: bool = False):
        # default state values
        self.daily_word: str = ""

        self.guessed_words: List[str] = []
        self.guess_results: List[List[int]] = []
        self.guesser_ids: List[int] = []
        self.guesser_names: List[str] = []
        self.correct_guess: bool = self.daily_word in self.guessed_words

        self.known_letters: Set[str] = set()
        self.unknown_letters: Set[str] = set(string.ascii_uppercase)

        self.start_time: datetime = datetime.now()
        self.time_taken: Optional[str] = None

        self.state_file_path: str = "data/wordle_state.json"
        self.load_state()

        self.wordle_stats: WordleStats = wordle_stats
        self.testing: bool = testing

        self.valid_words = set(np.genfromtxt('./data/valid-words.csv', delimiter=',', dtype=str).flatten())
        self.word_bank = list(np.genfromtxt('./data/word-bank.csv', delimiter=',', dtype=str))

        # Apparently I am a potato according to Brian :pensive:
        self.whitelisted_words = set(np.genfromtxt('./data/whitelisted-words.csv', delimiter=',', dtype=str))
        self.word_bank.extend(self.whitelisted_words)
    
    def pick_new_word(self) -> None:

        random_word = str(random.sample(self.word_bank, 1)[0])
        self.daily_word = random_word.upper()
        
        self.guessed_words: List[str] = []
        self.guess_results: List[List[int]] = []
        self.guesser_ids: List[int] = []
        self.guesser_names: List[str] = []
        self.correct_guess: bool = False

        self.known_letters: Set[str] = set()
        self.unknown_letters: Set[str] = set(string.ascii_uppercase)
        
        self.start_time: datetime = datetime.now()
        self.time_taken: Optional[str] = None

        self.wordle_stats.increment_games_played()
        self.save_state()

    def guess_word(self, ctx: discord.Interaction, word: str) -> None:
        guessed_word = word.strip().upper()

        self.check_valid_guess(guessed_word, ctx.user)

        self.guesser_ids.append(ctx.user.id)
        self.guesser_names.append(ctx.user.name)
        self.guessed_words.append(guessed_word)
        self.guess_results.append(self.wordle_logic(guessed_word))
        self.correct_guess = guessed_word == self.daily_word

        # starts the timer once the first guess is made
        if len(self.guessed_words) == 1:
            self.start_time = datetime.now()

        if self.correct_guess:
            time_taken = datetime.now() - self.start_time
            self.time_taken = timedelta_format(time_taken)
            self.wordle_stats.handle_win(len(self.guessed_words), time_taken)
        self.save_state()

    def check_valid_guess(self, guessed_word, user: Union[discord.User, discord.Member])-> None:
        """
        raises error if guessed word is invalid
        :param guessed_word: The word that is being checked.
        :param user: user making the guess.
        """
        if self.correct_guess:
            raise ValueError("The daily wordle has already been guessed")

        if not self.testing:
            if user.id in self.guesser_ids:
                raise ValueError(f"{user.display_name} has already guessed")
            if guessed_word not in self.whitelisted_words:
                if not len(guessed_word) == 5:
                    raise ValueError("The word must be 5 letters long")
                if guessed_word.lower() not in self.valid_words:
                    raise ValueError(f'"{guessed_word}" is not a valid word')
        if guessed_word in self.guessed_words:
            raise ValueError(f'"{guessed_word}" has already been guessed')

    def wordle_logic(self, guessed_word: str) -> List[int]:
        """
        Function to handle wordle logic
        :param guessed_word: The word that is being checked
        :return: String of red, yellow and red squares depending on the guessed word
        :
        """
        # Initialize result with all red squares
        guess_result = [0] * len(guessed_word)
        yellow_checker = list(self.daily_word)

        # Check for correct letters
        for index, letter in enumerate(guessed_word):
            if index >= len(self.daily_word):
                break
            if letter == self.daily_word[index]:
                guess_result[index] = 2
                # if a letter is found, we don't want it to be found again
                yellow_checker.remove(letter)
                self.known_letters.add(letter)

        # Check for letters that are in the word, but in the wrong place
        for index, letter in enumerate(guessed_word):
            if index < len(self.daily_word) and letter == self.daily_word[index]:
                continue
            if letter in yellow_checker:
                guess_result[index] = 1
                yellow_checker.remove(letter)
                self.known_letters.add(letter)

        # Remove unused letters from available letters
        for letter in guessed_word:
            if letter in self.unknown_letters:
                self.unknown_letters.remove(letter)

        return guess_result

    def get_dict_of_data(self) -> dict:
        return {
            "daily_word": self.daily_word,
            "guessed_words": list(self.guessed_words),
            "guesser_ids": list(self.guesser_ids),
            "guesser_names": list(self.guesser_names),
            "new_word_time": self.start_time.isoformat(),
            "time_taken": self.time_taken
        }

    def retrieve_data_from_dict(self, data: dict) -> None:
        self.daily_word = data.get("daily_word", "")
        self.guessed_words = data.get("guessed_words", [])
        self.correct_guess = self.daily_word in self.guessed_words
        for word in self.guessed_words:
            self.guess_results.append(self.wordle_logic(word))

        self.guesser_ids = data.get("guesser_ids", [])
        self.guesser_names = data.get("guesser_names", [])
        
        new_word_time_str = data.get("new_word_time", datetime.now().isoformat())
        self.start_time = datetime.fromisoformat(new_word_time_str)
        self.time_taken = data.get("time_taken", None)

    def save_state(self) -> None:
        """Save the current state to a JSON file."""
        with open(self.state_file_path, 'w') as file:
            json.dump(self.get_dict_of_data(), file)

    def load_state(self) -> None:
        """Load the state from a JSON file if it exists, otherwise set a new word."""
        if os.path.exists(self.state_file_path):
            with open(self.state_file_path, 'r') as file:
                wordle_dict = json.load(file)
                self.retrieve_data_from_dict(wordle_dict)
        else:
            self.pick_new_word()
