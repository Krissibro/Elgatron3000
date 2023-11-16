import numpy as np
import random
from utilities.shared import *
from utilities.settings import testing

valid_words = set(np.genfromtxt('./data/valid-words.csv', delimiter=',', dtype=str).flatten())
word_bank = list(np.genfromtxt('./data/word-bank.csv', delimiter=',', dtype=str))


class Wordle:
    daily_word = ""
    correct_guess = False
    guessed_words = set()
    users_that_guessed = set()
    available_letters = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                         't', 'u', 'v', 'w', 'x', 'y', 'z'}

    display_list = []

    async def pick_new_word(self):
        self.daily_word = random.sample(word_bank, 1)[0]
        self.guessed_words.clear()
        self.users_that_guessed.clear()
        self.display_list.clear()
        self.correct_guess = False

        if testing:
            # Test channel
            channel = client.get_channel(839100318893211669)
        else:
            # Gammin
            channel = client.get_channel(1111353625638350893)
        embed = discord.Embed(title="New Daily Wordle dropped! :fire: :fire: ")
        embed.description = (f"[Connections](https://www.nytimes.com/games/connections)\n" +
                             f"[Real Wordle](https://www.nytimes.com/games/wordle/index.html)")
        await channel.send(embed=embed)

    async def guess_word(self, ctx, guessed_word: str):
        guessed_word = guessed_word.strip().lower()

        if self.correct_guess:
            await ctx.response.send_message(embed=discord.Embed(title="The daily wordle has already been guessed"))
            return
        if not len(guessed_word) == 5:
            await ctx.response.send_message(embed=discord.Embed(title="The word must be 5 letters long"))
            return
        if not testing:
            if ctx.user.id in self.users_that_guessed:
                await ctx.response.send_message(embed=discord.Embed(title="You have already guessed"))
                return
            if guessed_word not in valid_words:
                await ctx.response.send_message(embed=discord.Embed(title=f"{guessed_word.upper()} is not a valid word"))
                return

        self.guessed_words.add(guessed_word)
        self.users_that_guessed.add(ctx.user.id)
        self.correct_guess = guessed_word == self.daily_word

        guess_result = [":red_square:"] * 5
        wrong_spot = []
        daily_word = list(self.daily_word)

        # check for correct placements
        for index, letter in enumerate(guessed_word):
            # Check if there are any letters in the right place, if not, add to list to be checked in next step
            if letter == daily_word[len(wrong_spot)]:
                guess_result[index] = ":green_square:"
                del daily_word[len(wrong_spot)]
            else:
                # to check in the next step
                wrong_spot.append(guessed_word[index])

        # check for letters in the wrong position
        for index, letter in enumerate(wrong_spot):
            if letter in daily_word:
                # if a letter is found, we don't want it to be found again
                guess_result[index] = ":yellow_square:"
                daily_word.remove(letter)

        # Four whitespaces
        seperator = "\u00A0\u00A0\u00A0\u00A0"
        self.display_list.append([ctx.user.id, seperator.join(guessed_word.upper()), ' '.join(guess_result)])

        await ctx.response.send_message(embed=await self.make_embed())

    async def make_embed(self):
        if self.correct_guess:
            embed = discord.Embed(title=f"Congratulations! The word was {self.daily_word.upper()}!")
        else:
            embed = discord.Embed(title=f"Daily Wordle")

        if not self.display_list:
            embed.description = "No guesses yet"
            return embed

        for user_id, guessed_word, guess_result in self.display_list:
            user = await client.fetch_user(user_id)
            embed.add_field(name=f"‎ **{guessed_word}**     <-  {user.name}",
                            value=f"{guess_result}",
                            inline=False)
            embed.set_footer(text=await self.format_available_letters())

        return embed

    async def format_available_letters(self):
        available_letters_list = [string.upper() for string in sorted(list(self.available_letters))]
        return f"Available letters:\n{' '.join(available_letters_list[:-1])} and {available_letters_list[-1]}"


wordle = Wordle()


async def initialize_wordle():
    global wordle

    trigger = CronTrigger(hour=8, minute=0, second=0, timezone='Europe/Oslo')

    await wordle.pick_new_word()
    scheduler.add_job(wordle.pick_new_word, trigger)

    scheduler.print_jobs()


@tree.command(
    name="daily_wordle",
    description="See the current progress of the daily wordle!",
    guild=discord.Object(id=guild_id)
)
async def daily_wordle(ctx):
    global wordle
    await ctx.response.send_message(embed=await wordle.make_embed())


@tree.command(
    name="guess_daily_wordle",
    description="Attempt to guess the daily wordle!",
    guild=discord.Object(id=guild_id)
)
async def guess_daily_wordle(ctx, guessed_word: str):
    global wordle

    await wordle.guess_word(ctx, guessed_word)
