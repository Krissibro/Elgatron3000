import pandas as pd
import random
from utilities.shared import *


valid_words_df = pd.read_csv('./data/valid-words.csv', header=None)
word_bank_df = pd.read_csv('./data/word-bank.csv', header=None)

valid_words = set(valid_words_df[0].tolist())
word_bank = word_bank_df[0].tolist()


class Wordle:
    daily_word = ""
    correct_guess = False
    guessed_words = set()
    users_that_guessed = set()

    display_list = []

    async def pick_new_word(self):
        self.daily_word = random.sample(word_bank, 1)[0]
        self.guessed_words.clear()
        self.users_that_guessed.clear()
        self.display_list.clear()
        self.correct_guess = False

        # Gammin
        #channel = client.get_channel(1111353625638350893)
        # Test channel
        channel = client.get_channel(839100318893211669)
        embed = discord.Embed(title="New Daily Wordle dropped! :fire: :fire: ")
        embed.add_field(name="There is also:", value=f"[Connections](https://www.nytimes.com/games/connections)\n" +
                                                      f"[Real Wordle](https://www.nytimes.com/games/wordle/index.html)")
        await channel.send(embed=embed)

    async def guess_word(self, ctx, guessed_word: str):
        guessed_word = guessed_word.strip().lower()

        if self.correct_guess:
            await ctx.response.send_message(embed=discord.Embed(title="The daily wordle has already been guessed"))
            return
        #if ctx.user.id in self.users_that_guessed:
        #    await ctx.response.send_message(embed=discord.Embed(title="You have already guessed"))
        #    return
        if not len(guessed_word) == 5:
            await ctx.response.send_message(embed=discord.Embed(title="The word must be 5 letters long"))
            return
        if guessed_word not in valid_words:
            await ctx.response.send_message(embed=discord.Embed(title=f"{guessed_word.upper()} is not a valid word"))
            return

        self.guessed_words.add(guessed_word)
        self.users_that_guessed.add(ctx.user.id)

        if guessed_word == self.daily_word:
            self.correct_guess = True
            await ctx.response.send_message(embed=discord.Embed(
                title=f"Congratulations! The word was {self.daily_word}!"))

        guess_result = []
        yellow_checker = list(self.daily_word)

        for index, letter in enumerate(guessed_word):
            # Check if there are any letters in the right place
            if letter == self.daily_word[index]:
                guess_result.append(":green_square:")

            # Check if the letter is in the word, and avoid duplicate yellows with yellow_checker
            elif letter in self.daily_word:
                if letter in yellow_checker:
                    yellow_checker.remove(letter)
                    guess_result.append(":yellow_square:")
                else:
                    guess_result.append(":red_square:")

            # If no match
            else:
                guess_result.append(":red_square:")

        # Three whitespaces
        seperator = "\u00A0\u00A0\u00A0\u00A0"
        self.display_list.append([ctx.user.id, seperator.join(guessed_word.upper()), ' '.join(guess_result)])         # TODO: Add 2 whitespaces before the first letter

        await ctx.response.send_message(embed=await self.make_embed())

    async def make_embed(self):
        embed = discord.Embed(title=f"Daily Wordle")

        if not self.display_list:
            embed.description = "No guesses yet"
            return embed

        for user_id, guessed_word, guess_result in self.display_list:
            user = await client.fetch_user(user_id)
            embed.add_field(name=f"‎ **{guessed_word}**     <-  {user.name}",
                            value=f"{guess_result}",
                            inline=False)

        return embed


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





