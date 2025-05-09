import json
import os
import random
import numpy as np
import discord

from datetime import datetime
from typing import Optional

from command_objects.WordleStats import WordleStats
from utilities.helper_functions import format_millisecond_duration
from utilities.settings import testing_channel_id, testing, wordle_channel_id

valid_words = set(np.genfromtxt('./data/valid-words.csv', delimiter=',', dtype=str).flatten())
word_bank = list(np.genfromtxt('./data/word-bank.csv', delimiter=',', dtype=str))

# Apparently I am a potato according to Brian :pensive:
whitelisted_words = set(np.genfromtxt('./data/whitelisted-words.csv', delimiter=',', dtype=str))
word_bank.extend(whitelisted_words)


class Wordle:
    def __init__(self, bot):

        self.state_file_path = "data/wordle_state.json"

        self.daily_word = ""
        self.correct_guess = False
        self.guessed_words = set()
        self.users_that_guessed = set()
        self.known_letters = set()
        self.available_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.display_list = []
        self.new_word_time = datetime.now()
        self.correct_guess_time = None

        channel = testing_channel_id if testing else wordle_channel_id
        self.channel = bot.get_channel(channel)

        self.wordle_stats = WordleStats()

    async def pick_new_word(self) -> None:
        if not self.correct_guess and not self.daily_word == "":

            if self.wordle_stats.correct_guess_streak > 0:
                await self.channel.send(embed=discord.Embed(
                    title=f"No one guessed the word! {self.daily_word.upper()}!  :sob:",
                    description=f"The word was **[{self.daily_word.upper()}](https://www.merriam-webster.com/dictionary/{self.daily_word.upper()})** \n\nGuess streak of   **{self.wordle_stats.correct_guess_streak}**   has been reset",
                    color=discord.Color.red()
                ))
            else:
                await self.channel.send(embed=discord.Embed(
                    title=f"No one guessed the word! :sob:",
                    description=f"The word was **[{self.daily_word.upper()}](https://www.merriam-webster.com/dictionary/{self.daily_word.upper()})**",
                    color=discord.Color.red()
                ))

            self.wordle_stats.reset_streak()

        random_word = str(random.sample(word_bank, 1)[0])
        self.daily_word = random_word.upper()
        # self.daily_word = "XOXOX"
        self.correct_guess = False
        self.guessed_words.clear()
        self.users_that_guessed.clear()
        self.known_letters.clear()
        self.available_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.display_list.clear()
        self.new_word_time = datetime.now()
        self.correct_guess_time = None
        print(self.daily_word)

        embed = discord.Embed(title="New Daily Wordle dropped! :fire: :fire: ")
        embed.description = ("[Connections](https://www.nytimes.com/games/connections)\n" +
                             "[Real Wordle](https://www.nytimes.com/games/wordle/index.html)\n" +
                             "[Pokedoku](https://pokedoku.com/)")

        if not testing:  # send embed if not testing
            await self.channel.send(embed=embed)

        self.wordle_stats.increment_games_played()
        self.save_state()

    async def guess_word(self, ctx: discord.Interaction, word: str) -> discord.Embed:
        guessed_word = word.strip().upper()

        invalid_guess_embed = self.check_valid_guess(guessed_word, ctx)
        if invalid_guess_embed:
            return invalid_guess_embed

        self.guessed_words.add(guessed_word)
        self.users_that_guessed.add(ctx.user.id)
        self.correct_guess = guessed_word == self.daily_word

        # Four whitespaces
        seperator = "\u00A0\u00A0\u00A0\u00A0"
        guess_result = self.wordle_logic(guessed_word)
        formatted_word = seperator.join(guessed_word)

        self.display_list.append([ctx.user.name, formatted_word, guess_result])


        if self.correct_guess:
            self.correct_guess_time = datetime.now()
            self.wordle_stats.handle_win(len(self.display_list), self.new_word_time, self.correct_guess_time)

        self.save_state()

        embed = await self.make_embed()
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

        if not testing:
            if ctx.user.id in self.users_that_guessed:
                return discord.Embed(title=f"{ctx.user.display_name} has already guessed")
            if guessed_word not in whitelisted_words:
                if not len(guessed_word) == 5:
                    return discord.Embed(title="The word must be 5 letters long")
                if guessed_word.lower() not in valid_words:
                    return discord.Embed(title=f'"{guessed_word}" is not a valid word')
        if guessed_word in self.guessed_words:
            return discord.Embed(title=f'"{guessed_word}" has already been guessed')


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
            if letter in self.available_letters:
                self.available_letters.remove(letter)

        return ' '.join(guess_result)


    async def make_embed(self) -> discord.Embed:
        if self.correct_guess:
            embed = discord.Embed(title=f"Congratulations!", color=discord.Color.green(), description=f"The word was **[{self.daily_word.upper()}](https://www.merriam-webster.com/dictionary/{self.daily_word})**!")
            embed.add_field(name=f"Guess streak:   ",
                            value=f"{self.wordle_stats.correct_guess_streak} days")
            if self.correct_guess_time:
                time_difference = self.correct_guess_time - self.new_word_time
                total_milliseconds = int(time_difference.total_seconds() * 1000)
                formatted_time = format_millisecond_duration(total_milliseconds)
                embed.add_field(name=f"Time spent:   ",
                                value=f"{formatted_time}", inline=False)

            embed.add_field(name="", value="", inline=False)

        else:
            embed = discord.Embed(title="Daily Wordle")

        if not self.display_list:
            embed.description = "No guesses yet"
            return embed

        for username, guessed_word, guess_result in self.display_list:
            # user = await client.fetch_user(user_id)
            embed.add_field(name=f"‎ **{guessed_word}**     <-  {username}",
                            value=f"{guess_result}",
                            inline=False)
            embed.set_footer(text=self.format_available_letters())

        return embed


    async def make_stats_embed(self) -> discord.Embed:
        return await self.wordle_stats.make_embed()

    async def send_reminder(self) -> None:
        if not self.correct_guess:
            embed = discord.Embed(title="Me when the and I and me when is and it",
                                  description="Uhhh:sob: :sob:")
            await self.channel.send(embed=embed)


    def format_available_letters(self) -> str:
        sorted_available_letters = sorted(list(self.available_letters))
        sorted_known_letters = sorted(list(self.known_letters))
        known_letters = f"Known letters:\n{' '.join(sorted_known_letters)}"
        rest = f"Available letters:\n{' '.join(sorted_available_letters)}"
        return f"{known_letters}\n{rest}"


    def get_dict_of_data(self) -> dict:
        return {
            "daily_word": self.daily_word,
            "correct_guess": self.correct_guess,
            "guessed_words": list(self.guessed_words),
            "users_that_guessed": list(self.users_that_guessed),
            "known_letters": list(self.known_letters),
            "available_letters": list(self.available_letters),
            "display_list": self.display_list,
            "new_word_time": self.new_word_time.isoformat(),
            "correct_guess_time": self.correct_guess_time.isoformat() if self.correct_guess_time else None,
        }

    def retrieve_data_from_dict(self, data) -> None:
        self.daily_word = data.get("daily_word", "")
        self.correct_guess = data.get("correct_guess", False)
        self.guessed_words = set(data.get("guessed_words", []))
        self.users_that_guessed = set(data.get("users_that_guessed", []))
        self.known_letters = set(data.get("known_letters", []))
        self.available_letters = set(data.get("available_letters", list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')))
        self.display_list = data.get("display_list", [])
        new_word_time_str = data.get("new_word_time")
        correct_guess_time_str = data.get("correct_guess_time")
        self.new_word_time = datetime.fromisoformat(new_word_time_str) if new_word_time_str else datetime.now()
        self.correct_guess_time = datetime.fromisoformat(correct_guess_time_str) if correct_guess_time_str else None

    def save_state(self) -> None:
        """Save the current state to a JSON file."""
        with open(self.state_file_path, 'w') as file:
            json.dump(self.get_dict_of_data(), file)

    async def load_state(self) -> None:
        """Load the state from a JSON file if it exists, otherwise set a new word."""
        if os.path.exists(self.state_file_path):
            with open(self.state_file_path, 'r') as file:
                wordle_dict = json.load(file)
                self.retrieve_data_from_dict(wordle_dict)
        else:
            await self.pick_new_word()