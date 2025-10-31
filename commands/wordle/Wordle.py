import json
import os
import random
import string
import numpy as np
import discord

from datetime import datetime
from typing import List, Optional, Set

from apscheduler.triggers.cron import CronTrigger

from commands.wordle.WordleStats import WordleStats
from utilities.elgatron import Elgatron
from utilities.helper_functions import timedelta_format
from utilities.settings import testing_channel_id, wordle_channel_id
from utilities.validators import validate_text_channel

valid_words = set(np.genfromtxt('./data/valid-words.csv', delimiter=',', dtype=str).flatten())
word_bank = list(np.genfromtxt('./data/word-bank.csv', delimiter=',', dtype=str))

# Apparently I am a potato according to Brian :pensive:
whitelisted_words = set(np.genfromtxt('./data/whitelisted-words.csv', delimiter=',', dtype=str))
word_bank.extend(whitelisted_words)


class Wordle:
    def __init__(self, bot: Elgatron):
        self.bot: Elgatron = bot
        # default state values
        self.daily_word: str = ""
        self.correct_guess: bool = False
        self.guessed_words: List[str] = []
        self.guess_results: List[str] = []
        self.guesser_ids: List[int] = []
        self.guesser_names: List[str] = []
        self.known_letters: Set[str] = set()
        self.unknown_letters: Set[str] = set(string.ascii_uppercase)
        self.new_word_time: datetime = datetime.now()
        self.time_taken: Optional[str] = None

        self.state_file_path: str = "data/wordle_state.json"
        self.load_state(self.state_file_path)

        self.channel_id = testing_channel_id if bot.testing else wordle_channel_id

        new_word_trigger = CronTrigger(hour=8, minute=0, second=0, timezone='Europe/Oslo')
        bot.scheduler.add_job(self.pick_new_word, new_word_trigger, id="wordle_pick_new_word")
        
        reminder_trigger = CronTrigger(hour=22, minute=0, second=0, timezone='Europe/Oslo')
        bot.scheduler.add_job(self.send_reminder, reminder_trigger, id="wordle_reminder")

        # TODO this does not work since commands are loaded before the bot is connected
        # the channel stuff should probably just use the command context to get the channel
        # i have replaced self.channel with self.bot.get_channel(self.channel_id) for now
        # self.channel = self.bot.get_channel(channel)

        self.wordle_stats: WordleStats = WordleStats()

    
    def pick_new_word(self) -> None:

        random_word = str(random.sample(word_bank, 1)[0])
        self.daily_word = random_word.upper()
        self.correct_guess: bool = False
        
        self.guessed_words: List[str] = []
        self.guess_results: List[str] = []
        self.guesser_ids:   List[int] = []
        self.guesser_names: List[str] = []

        self.known_letters:     Set[str] = set()
        self.unknown_letters: Set[str] = set(string.ascii_uppercase)
        
        self.new_word_time: datetime = datetime.now()
        self.time_taken: Optional[str] = None


        self.wordle_stats.increment_games_played()
        self.save_state()

    def guess_word(self, ctx: discord.Interaction, word: str) -> discord.Embed:
        guessed_word = word.strip().upper()

        invalid_guess_embed = self.check_valid_guess(guessed_word, ctx)
        if invalid_guess_embed:
            return invalid_guess_embed

        self.guesser_ids.append(ctx.user.id)
        self.guesser_names.append(ctx.user.name)
        self.guessed_words.append(guessed_word)
        self.guess_results.append(self.wordle_logic(guessed_word))
        self.correct_guess = guessed_word == self.daily_word

        if self.correct_guess:
            time_taken = datetime.now() - self.new_word_time
            self.time_taken = timedelta_format(time_taken)
            self.wordle_stats.handle_win(len(self.guessed_words), time_taken)
        self.correct_guess = guessed_word == self.daily_word
        self.save_state()

        embed = self.make_embed()
        return embed

    def check_valid_guess(self, guessed_word, ctx) -> Optional[discord.Embed]:
        """
        checks whether the guess is valid
        :param guessed_word: The word that is being checked
        :param ctx: discord context
        :return: None if the guess is valid, else an embed containing the reason the guess is invalid
        """
        if self.correct_guess:
            return discord.Embed(title="The daily wordle has already been guessed")

        if not self.bot.testing:
            if ctx.user.id in self.guesser_ids:
                return discord.Embed(title=f"{ctx.user.display_name} has already guessed")
            if guessed_word not in whitelisted_words:
                if not len(guessed_word) == 5:
                    return discord.Embed(title="The word must be 5 letters long")
                if guessed_word.lower() not in valid_words:
                    return discord.Embed(title=f'"{guessed_word}" is not a valid word')
        if guessed_word in self.guessed_words:
            return discord.Embed(title=f'"{guessed_word}" has already been guessed')
        return None

    def wordle_logic(self, guessed_word: str) -> str:
        """
        Function to handle wordle logic
        :param guessed_word: The word that is being checked
        :return: String of red, yellow and red squares depending on the guessed word
        :
        """
        # Initialize result with all red squares
        guess_result = [":red_square:"] * len(guessed_word)
        yellow_checker = list(self.daily_word)

        # Check for correct letters
        for index, letter in enumerate(guessed_word):
            if index >= len(self.daily_word):
                break
            if letter == self.daily_word[index]:
                guess_result[index] = ":green_square:"
                # if a letter is found, we don't want it to be found again
                yellow_checker.remove(letter)
                self.known_letters.add(letter)

        # Check for letters that are in the word, but in the wrong place
        for index, letter in enumerate(guessed_word):
            if index < len(self.daily_word) and letter == self.daily_word[index]:
                continue
            if letter in yellow_checker:
                guess_result[index] = ":yellow_square:"
                yellow_checker.remove(letter)
                self.known_letters.add(letter)

        # Remove unused letters from available letters
        for letter in guessed_word:
            if letter in self.unknown_letters:
                self.unknown_letters.remove(letter)

        return ' '.join(guess_result)


    def make_embed(self) -> discord.Embed:
        if self.correct_guess:
            embed = discord.Embed(title=f"Congratulations!", color=discord.Color.green(), description=f"The word was **[{self.daily_word.upper()}](https://www.merriam-webster.com/dictionary/{self.daily_word})**!")
            embed.add_field(name=f"Win streak:   ",
                            value=f"{self.wordle_stats.win_streak} days")
            
            if self.time_taken:
                embed.add_field(name=f"Time spent:   ",
                                value=f"{self.time_taken}", inline=False)

            embed.add_field(name="", value="", inline=False)

        else:
            embed = discord.Embed(title="Daily Wordle")

        embed.set_footer(text=self.format_available_letters())

        if not self.guessed_words:
            embed.description = "No guesses yet"
            return embed

        for username, guessed_word, guess_result in zip(self.guesser_names, self.guessed_words, self.guess_results):
            # format word
            seperator = "\u00A0\u00A0\u00A0\u00A0"
            formatted_word = seperator.join(guessed_word)

            embed.add_field(name=f"‎ **{formatted_word}**     <-  {username}",
                            value=f"{guess_result}",
                            inline=False)
            embed.set_footer(text=self.format_available_letters())

        return embed

    def make_stats_embed(self) -> discord.Embed:
        return self.wordle_stats.make_embed()

    async def send_reminder(self) -> None:
        channel = validate_text_channel(self.bot.get_channel(self.channel_id))
        if isinstance(channel, discord.Embed):
            raise ValueError("The channel ID provided does not correspond to a text channel.")

        if not self.correct_guess:
            embed = discord.Embed(title="Me when the and I and me when is and it",
                                  description="Uhhh:sob: :sob:")
            await channel.send(embed=embed)

    async def start_new_game(self) -> None:
        channel = validate_text_channel(self.bot.get_channel(self.channel_id))
        if isinstance(channel, discord.Embed):
            raise ValueError("The channel ID provided does not correspond to a text channel.")

        if not self.correct_guess and not self.daily_word == "":
            description = f"The word was **[{self.daily_word.upper()}](https://www.merriam-webster.com/dictionary/{self.daily_word.upper()})**"
            if self.wordle_stats.win_streak > 0:
                description += f"\n\nWin streak of   **{self.wordle_stats.win_streak}**   has been reset"
            
            await channel.send(embed=discord.Embed(
                title=f"No one guessed the word! :sob:",
                description=description,
                color=discord.Color.red()
            ))
    
            self.wordle_stats.reset_streak()

        self.pick_new_word()

        if self.bot.testing:
            print(self.daily_word)

        embed = discord.Embed(title="New Daily Wordle dropped! :fire: :fire: ")
        embed.description = ("[Connections](https://www.nytimes.com/games/connections)\n" +
                             "[Real Wordle](https://www.nytimes.com/games/wordle/index.html)\n" +
                             "[Pokedoku](https://pokedoku.com/)")

        if not self.bot.testing:  # send embed if not testing
            await channel.send(embed=embed)

    def format_available_letters(self) -> str:
        sorted_known_letters = sorted(list(self.known_letters))
        sorted_available_letters = sorted(list(self.unknown_letters))
        known_letters = f"Known letters:\n{' '.join(sorted_known_letters)}"
        unknown_letters = f"Available letters:\n{' '.join(sorted_available_letters)}"
        return f"{known_letters}\n{unknown_letters}"


    def get_dict_of_data(self) -> dict:
        return {
            "daily_word": self.daily_word,
            "correct_guess": self.correct_guess,
            "guessed_words": list(self.guessed_words),
            "guess_results": self.guess_results,
            "guesser_ids": list(self.guesser_ids),
            "guesser_names": list(self.guesser_names),
            "known_letters": list(self.known_letters),
            "unknown_letters": list(self.unknown_letters),
            "new_word_time": self.new_word_time.isoformat(),
            "time_taken": self.time_taken
        }

    def retrieve_data_from_dict(self, data: dict) -> None:
        self.daily_word = data.get("daily_word", "")
        self.correct_guess = data.get("correct_guess", False)
        self.guessed_words = data.get("guessed_words", [])
        self.guesser_ids = data.get("guesser_ids", [])
        self.guesser_names = data.get("guesser_names", [])
        self.guess_results = data.get("guess_results", [])
        self.known_letters = set(data.get("known_letters", []))
        self.unknown_letters = set(data.get("unknown_letters", list(string.ascii_uppercase)))
        
        new_word_time_str = data.get("new_word_time", datetime.now().isoformat())
        self.new_word_time = datetime.fromisoformat(new_word_time_str)
        self.time_taken = data.get("time_taken", None)

    def save_state(self) -> None:
        """Save the current state to a JSON file."""
        with open(self.state_file_path, 'w') as file:
            json.dump(self.get_dict_of_data(), file)

    def load_state(self, path) -> None:
        """Load the state from a JSON file if it exists, otherwise set a new word."""
        if os.path.exists(path):
            with open(path, 'r') as file:
                wordle_dict = json.load(file)
                self.retrieve_data_from_dict(wordle_dict)
        else:
            self.pick_new_word()