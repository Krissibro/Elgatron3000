import json
import os
import discord
from discord import app_commands
from discord.ext import commands
import random
import numpy as np

from commands.wordle_stats import WordleStats

from apscheduler.triggers.cron import CronTrigger

from utilities.settings import testing, wordle_channel_id, guild_id, testing_channel_id
from utilities.settings import bot, scheduler

valid_words = set(np.genfromtxt('./data/valid-words.csv', delimiter=',', dtype=str).flatten())
word_bank = list(np.genfromtxt('./data/word-bank.csv', delimiter=',', dtype=str))

# Apparently I am a potato according to Brian :pensive:
whitelisted_words = set(np.genfromtxt('./data/whitelisted-words.csv', delimiter=',', dtype=str))
word_bank.extend(whitelisted_words)


@app_commands.guild_only()
class Wordle(commands.GroupCog, group_name="wordle"):
    state_file_path = "data/wordle_state.json"

    daily_word = ""
    correct_guess = False
    guessed_words = set()
    users_that_guessed = set()
    known_letters = set()
    available_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    display_list = []

    wordle_stats = WordleStats()

    async def pick_new_word(self) -> None:
        if not self.correct_guess and not self.daily_word == "":
            channel = testing_channel_id if testing else wordle_channel_id

            if self.wordle_stats.correct_guess_streak > 0:
                await bot.get_channel(channel).send(embed=discord.Embed(
                    title=f"No one guessed the word {self.daily_word.upper()}!  :sob:",
                    description=f"Guess streak of  **{self.wordle_stats.correct_guess_streak}**  has been reset"))
            else:
                await bot.get_channel(channel).send(embed=discord.Embed(
                    title=f"No one guessed the word {self.daily_word.upper()}!  :sob:"))

            self.wordle_stats.reset_streak()

        random_word = str(random.sample(word_bank, 1)[0])
        self.daily_word = random_word.upper()
        # self.daily_word = "XOXOX"
        print(self.daily_word)
        self.guessed_words.clear()
        self.users_that_guessed.clear()
        self.display_list.clear()
        self.known_letters.clear()
        self.available_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.correct_guess = False

        if not testing:
            # channel = client.get_channel(testing_channel_id)      # Test channel
            channel = bot.get_channel(wordle_channel_id)  # Gaming channel

            embed = discord.Embed(title="New Daily Wordle dropped! :fire: :fire: ")

            embed.description = ("[Connections](https://www.nytimes.com/games/connections)\n" +
                                 "[Real Wordle](https://www.nytimes.com/games/wordle/index.html)\n" +
                                 "[Pokedoku](https://pokedoku.com/)")
            await channel.send(embed=embed)

        self.wordle_stats.increment_games_played()
        self.save_state()

    @app_commands.command(
        name="guess",
        description="Attempt to guess the daily wordle!",
    )
    async def guess_word(self, ctx, word: str) -> None:
        guessed_word = word.strip().upper()

        if self.correct_guess:
            await ctx.response.send_message(embed=discord.Embed(title="The daily wordle has already been guessed"))
            return

        if not testing:
            if ctx.user.id in self.users_that_guessed:
                await ctx.response.send_message(embed=discord.Embed(title="You have already guessed"))
                return
            if guessed_word not in whitelisted_words:
                if not len(guessed_word) == 5:
                    await ctx.response.send_message(embed=discord.Embed(title="The word must be 5 letters long"))
                    return
                if guessed_word.lower() not in valid_words:
                    await ctx.response.send_message(embed=discord.Embed(title=f"{guessed_word} is not a valid word"))
                    return
            if guessed_word in self.guessed_words:
                await ctx.response.send_message(embed=discord.Embed(title=f"{guessed_word} has already been guessed"))
                return

        self.guessed_words.add(guessed_word)
        self.users_that_guessed.add(ctx.user.id)
        self.correct_guess = guessed_word == self.daily_word

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

        # Four whitespaces
        seperator = "\u00A0\u00A0\u00A0\u00A0"
        self.display_list.append([ctx.user.name, seperator.join(guessed_word), ' '.join(guess_result)])

        if self.correct_guess:
            self.wordle_stats.handle_win(len(self.display_list))

        self.save_state()

        await ctx.response.send_message(embed=await self.make_embed())

    @app_commands.command(
        name="current",
        description="See the current progress of the daily wordle!",
    )
    async def current_game(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed=await self.make_embed())

    async def make_embed(self) -> discord.Embed:
        if self.correct_guess:
            embed = discord.Embed(title=f"Congratulations! \nThe word was {self.daily_word}!")
            embed.add_field(name=f"Guess streak:   {self.wordle_stats.correct_guess_streak}",
                            value=f"\u200B")
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

    def format_available_letters(self) -> str:
        sorted_available_letters = sorted(list(self.available_letters))
        sorted_known_letters = sorted(list(self.known_letters))
        known_letters = f"Known letters:\n{' '.join(sorted_known_letters)}"
        rest = f"Available letters:\n{' '.join(sorted_available_letters)}"
        return f"{known_letters}\n{rest}"

    def get_dict_of_data(self):
        return {
            "daily_word": self.daily_word,
            "correct_guess": self.correct_guess,
            "guessed_words": list(self.guessed_words),
            "users_that_guessed": list(self.users_that_guessed),
            "known_letters": list(self.known_letters),
            "available_letters": list(self.available_letters),
            "display_list": self.display_list
        }

    def retrieve_data_from_dict(self, data):
        self.daily_word = data.get("daily_word", "")
        self.correct_guess = data.get("correct_guess", False)
        self.guessed_words = set(data.get("guessed_words", []))
        self.users_that_guessed = set(data.get("users_that_guessed", []))
        self.known_letters = set(data.get("known_letters", []))
        self.available_letters = set(data.get("available_letters", list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')))
        self.display_list = data.get("display_list", [])

    def save_state(self):
        """Save the current state to a JSON file."""
        with open(self.state_file_path, 'w') as file:
            json.dump(self.get_dict_of_data(), file)

    async def load_state(self):
        """Load the state from a JSON file if it exists, otherwise set a new word."""
        if os.path.exists(self.state_file_path):
            with open(self.state_file_path, 'r') as file:
                wordle_dict = json.load(file)
                self.retrieve_data_from_dict(wordle_dict)
        else:
            await self.pick_new_word()

    @app_commands.command(
        name="stats",
        description="See the wordle statistics!",
    )
    async def show_stats(self, ctx):
        await ctx.response.send_message(embed=self.wordle_stats.create_embed())

    if testing:
        @commands.is_owner()
        @app_commands.command(
            name="reset",
            description="Reset the daily wordle",
        )
        async def reset_wordle(self, ctx):
            await self.pick_new_word()
            await ctx.response.send_message(embed=discord.Embed(title="Wordle has been reset!"), ephemeral=True, delete_after=10)


async def setup(setup_bot):
    wordle_game = Wordle()
    await wordle_game.load_state()

    job_id = "wordle_pick_new_word"
    if not scheduler.get_job(job_id):
        trigger = CronTrigger(hour=8, minute=0, second=0, timezone='Europe/Oslo')
        scheduler.add_job(wordle_game.pick_new_word, trigger, id=job_id)

    await bot.add_cog(wordle_game, guild=bot.get_guild(guild_id))



