import discord
import random
import numpy as np

from apscheduler.triggers.cron import CronTrigger

from utilities.settings import testing, wordle_channel_id, guild_id, testing_channel_id
from utilities.settings import client, scheduler, tree
from utilities.state_helper import save_wordle_game_state, load_wordle_game_state


valid_words = set(np.genfromtxt('./data/valid-words.csv', delimiter=',', dtype=str).flatten())
word_bank = list(np.genfromtxt('./data/word-bank.csv', delimiter=',', dtype=str))

# Apparently I am a potato according to Brian :pensive:
whitelisted_words = set(np.genfromtxt('./data/whitelisted-words.csv', delimiter=',', dtype=str))
word_bank.extend(whitelisted_words)


class Wordle:
    daily_word = ""
    correct_guess = False
    correct_guess_streak = 0
    guessed_words = set()
    users_that_guessed = set()
    known_letters = set()
    available_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    display_list = []

    # Singleton pattern, only one instance of Wordle should exist
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Wordle, cls).__new__(cls)
            # Initialize any attributes of your instance here
            cls._instance.daily_word = ""
            cls._instance.correct_guess = False
            cls._instance.correct_guess_streak = 0
            cls._instance.guessed_words = set()
            cls._instance.users_that_guessed = set()
            cls._instance.known_letters = set()
            cls._instance.available_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            cls._instance.display_list = []
        return cls._instance

    async def pick_new_word(self) -> None:
        if not self.correct_guess and not self.daily_word == "":
            channel = testing_channel_id if testing else wordle_channel_id

            if self.correct_guess_streak > 0:
                await client.get_channel(channel).send(embed=discord.Embed(
                    title=f"No one guessed the word {self.daily_word.upper()}!  :sob:",
                    description=f"Guess streak of  **{self.correct_guess_streak}**  has been reset"))
            else:
                await client.get_channel(channel).send(embed=discord.Embed(
                    title=f"No one guessed the word {self.daily_word.upper()}!  :sob:"))

            self.correct_guess_streak = 0

        random_word = str(random.sample(word_bank, 1)[0])
        self.daily_word = random_word.upper()
        # self.daily_word = "XOXOX"
        print(self.daily_word)
        self.guessed_words.clear()
        self.users_that_guessed.clear()
        self.display_list.clear()
        self.known_letters.clear()
        self.available_letters = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}
        self.correct_guess = False

        if not testing:
            # channel = client.get_channel(testing_channel_id)      # Test channel
            channel = client.get_channel(wordle_channel_id)       # Gaming channel

            embed = discord.Embed(title="New Daily Wordle dropped! :fire: :fire: ")

            embed.description = ("[Connections](https://www.nytimes.com/games/connections)\n" +
                                 "[Real Wordle](https://www.nytimes.com/games/wordle/index.html)\n" +
                                 "[Pokedoku](https://pokedoku.com/)")
            await channel.send(embed=embed)

        save_wordle_game_state(self)

    async def guess_word(self, ctx, guessed_word: str) -> None:
        guessed_word = guessed_word.strip().upper()

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
        if self.correct_guess:
            self.correct_guess_streak += 1

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

        await ctx.response.send_message(embed=await self.make_embed())

        save_wordle_game_state(self)

    async def make_embed(self) -> discord.Embed:
        if self.correct_guess:
            embed = discord.Embed(title=f"Congratulations! \nThe word was {self.daily_word}!")
            embed.add_field(name=f"Guess streak:   {self.correct_guess_streak}",
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


wordle_game = Wordle()


async def initialize_wordle() -> None:
    # If the bot is restarted, the daily wordle will be reset
    global wordle_game
    wordle_game = await load_wordle_game_state()

    trigger = CronTrigger(hour=8, minute=0, second=0, timezone='Europe/Oslo')
    scheduler.add_job(wordle_game.pick_new_word, trigger)


@tree.command(
    name="wordle",
    description="See the current progress of the daily wordle!",
    guild=discord.Object(id=guild_id)
)
async def wordle(ctx):
    await ctx.response.send_message(embed=await wordle_game.make_embed())


@tree.command(
    name="guess_wordle",
    description="Attempt to guess the daily wordle!",
    guild=discord.Object(id=guild_id)
)
async def guess_wordle(ctx, guessed_word: str):
    await wordle_game.guess_word(ctx, guessed_word)



