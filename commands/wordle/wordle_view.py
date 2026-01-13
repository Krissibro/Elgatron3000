import discord

from typing import List, Set

from commands.wordle.wordle_stats import WordleStats
from commands.wordle.wordle_model import WordleModel
from utilities.elgatron import Elgatron

from utilities.validators import validate_messageable
from utilities.helper_functions import timedelta_format

class WordleView:

    def __init__(self, bot: Elgatron, wordle_model: WordleModel, wordle_stats: WordleStats, testing: bool = False):
        self.bot = bot
        self.wordle_model = wordle_model
        self.wordle_stats = wordle_stats
        self.testing = testing

        self.channel_id = bot.testing_channel_id if bot.testing else bot.wordle_channel_id

    def make_wordle_embed(self) -> discord.Embed:
        if self.wordle_model.correct_guess:
            embed = discord.Embed(title=f"Congratulations!", color=discord.Color.green(),
                                  description=f"The word was **[{self.wordle_model.daily_word.upper()}](https://www.merriam-webster.com/dictionary/{self.wordle_model.daily_word})**!")
            embed.add_field(name=f"Win streak:   ",
                            value=f"{self.wordle_stats.win_streak} days")

            if self.wordle_model.time_taken:
                embed.add_field(name=f"Time spent:   ",
                                value=f"{self.wordle_model.time_taken}", inline=False)

            embed.add_field(name="", value="", inline=False)

        else:
            embed = discord.Embed(title="Daily Wordle")

        if not self.wordle_model.guessed_words:
            embed.description = "No guesses yet"
            return embed

        for username, guessed_word, guess_result in zip(self.wordle_model.guesser_names, self.wordle_model.guessed_words, self.wordle_model.guess_results):
            # format word
            seperator = "\u00A0\u00A0\u00A0\u00A0"
            formatted_word = seperator.join(guessed_word)

            embed.add_field(name=f"‎ **{formatted_word}**     <-  {username}",
                            value=f"{self.format_word(guess_result)}",
                            inline=False)

        embed.set_footer(text=self.format_available_letters(self.wordle_model.known_letters, self.wordle_model.unknown_letters))
        return embed

    async def send_reminder(self) -> None:
        """Send reminder if game is not yet won"""
        channel = validate_messageable(self.bot.get_channel(self.channel_id))

        embed = discord.Embed(title="Me when the and I and me when is and it",
                              description="Uhhh:sob: :sob:")
        await channel.send(embed=embed)


    def make_stats_embed(self):
        percentage_wins = (
            f"{(self.wordle_stats.wins / self.wordle_stats.games_played * 100):.2f}"
            if self.wordle_stats.games_played > 0 else "0.00"
        )
        average_guesses = (self.wordle_stats.number_of_guesses / self.wordle_stats.wins) if self.wordle_stats.games_played > 0 and self.wordle_stats.wins > 0 else 0

        embed = discord.Embed(title="Wordle Stats", colour=discord.Colour.blue())
        embed.add_field(name="Games played", value=self.wordle_stats.games_played, inline=True)
        embed.add_field(name="Wins", value=f"{self.wordle_stats.wins} \u00A0\u00A0\u00A0 ({percentage_wins}%)", inline=True)
        embed.add_field(name="\t Number of guesses", value=self.wordle_stats.number_of_guesses, inline=True)
        embed.add_field(name="Average guesses", value=f"{average_guesses:.3f}", inline=True)
        embed.add_field(name="Current streak", value=self.wordle_stats.win_streak, inline=True)
        embed.add_field(name="Longest streak", value=self.wordle_stats.longest_win_streak, inline=True)

        if self.wordle_stats.fastest_win.total_seconds() > 0:
            embed.add_field(name="Fastest win", value=f"{timedelta_format(self.wordle_stats.fastest_win)}", inline=True)

        # if wins are less than or equal than 0, there is no reason to show the rest, it also breaks the math
        if self.wordle_stats.wins <= 0:
            return embed

        embed.add_field(name="\u200b", value="", inline=False)

        embed = self.add_guess_hist(embed)

        return embed

    def add_guess_hist(self, embed: discord.Embed) -> discord.Embed:
        highest_guess_count = max(self.wordle_stats.guess_distribution.values())
        highest_guess_percentage = (highest_guess_count / self.wordle_stats.wins) * 100

        sorted_guess_distribution = sorted(self.wordle_stats.guess_distribution.items(), key=lambda key: int(key[0]))
        for guess_amount, guess_count in sorted_guess_distribution:
            if guess_count == 0:
                continue
            percentage = (guess_count / self.wordle_stats.wins) * 100
            # Scale percentage to fit in max 14 squares per line, 14 is max that can fit on mobile
            square_count = int(percentage / highest_guess_percentage * 14 + 0.5)

            embed.add_field(
                name=f"{guess_amount} guesses:      {guess_count}   ({percentage:.2f}%)",
                value=square_count * ":blue_square:" if square_count > 0 else ":black_large_square:",
                inline=False
            )
        return embed

    @staticmethod
    def format_available_letters(known_letters: Set[str], unknown_letters: Set[str]) -> str:
        sorted_known_letters = sorted(list(known_letters))
        sorted_available_letters = sorted(list(unknown_letters))
        formatted_known_letters = f"Known letters:\n{' '.join(sorted_known_letters)}"
        formatted_unknown_letters = f"Available letters:\n{' '.join(sorted_available_letters)}"
        return f"{formatted_known_letters}\n{formatted_unknown_letters}"

    @staticmethod
    def format_word(result: List[int]) -> str:
        result_map = {0: ":red_square:", 1:":yellow_square:", 2:":green_square:"}
        return " ".join([result_map[result] for result in result])

    def make_game_over_embed(self, daily_word: str) -> discord.Embed:
        """Create embed for when no one guessed the word"""
        description = f"The word was **[{daily_word}](https://www.merriam-webster.com/dictionary/{daily_word})**"
        if self.wordle_stats.win_streak > 0:
            description += f"\n\nWin streak of   **{self.wordle_stats.win_streak}**   has been reset"

        return discord.Embed(
            title=f"No one guessed the word! :sob:",
            description=description,
            color=discord.Color.red()
        )

    @staticmethod
    def new_game_embed() -> discord.Embed:
        embed = discord.Embed(title="New Daily Wordle dropped! :fire: :fire:")
        embed.description = ("[Connections](https://www.nytimes.com/games/connections)\n" +
                             "[Real Wordle](https://www.nytimes.com/games/wordle/index.html)\n" +
                             "[Pokedoku](https://pokedoku.com/)")
        return embed