import string
import discord

from typing import List, Set, Iterable, Tuple

from app.commands.wordle.wordle_db import WordleDB
from app.core.elgatron import Elgatron

from app.models import WordleGame, WordleGuess
from app.models.wordle_model import WordleStats
from app.utilities.validators import validate_messageable
from app.utilities.helper_functions import timedelta_format, char_to_emoji
from app.commands.wordle.wordle_logic import wordle_logic

class WordleView:
    def __init__(self, bot: Elgatron, wordle_model: WordleDB):
        self.bot: Elgatron = bot
        self.wordle_db: WordleDB = wordle_model

        self.channel_id = bot.testing_channel_id if bot.testing else bot.wordle_channel_id

    async def make_wordle_embed(self, game: WordleGame) -> discord.Embed:
        if game.is_finished():
            embed = discord.Embed(title=f"Congratulations!", color=discord.Color.green(),
                                  description=f"The word was **[{game.word.upper()}](https://www.merriam-webster.com/dictionary/{game.word})**!")
            
            time_taken = game.time_taken()
            if time_taken is not None:
                embed.add_field(name=f"Time spent:   ",
                                value=f"{timedelta_format(time_taken)}", inline=False)

            embed.add_field(name="", value="", inline=False)
        else:
            embed = discord.Embed(title="Daily Wordle")

        if not game.guesses:
            embed.description = "No guesses yet"
            return embed

        fields, known_letters, unknown_letters = self.process_guesses(game.guesses, game.word)
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=False)

        embed.set_footer(
            text=self.format_available_letters(known_letters, unknown_letters)
        )
        return embed

    async def send_reminder(self) -> None:
        """Sends the reminder if game is not yet won"""
        channel = validate_messageable(self.bot.get_channel(self.channel_id))

        embed = discord.Embed(title="Me when the and I and me when is and it",
                              description="Uhhh:sob: :sob:")
        await channel.send(embed=embed)

    def process_guesses(self, guesses: Iterable[WordleGuess], solution: str) -> Tuple[List[Tuple[str, str]], Set[str], Set[str]]:
        known_letters: Set[str] = set()
        unknown_letters = set(string.ascii_uppercase)
        fields: List[Tuple[str, str]] = []

        for guess in guesses:
            result = wordle_logic(guess.word, solution)

            # Track letters
            for letter, score in zip(guess.word, result):
                unknown_letters.discard(letter)
                if score:
                    known_letters.add(letter)

            # Build embed field
            fields.append((
                f"{char_to_emoji(guess.word)}     <-  {guess.guesser_name}",
                self.format_word(result)
            ))
        return fields, known_letters, unknown_letters

    def make_stats_embed(self, stats: WordleStats)-> discord.Embed:
        percentage_wins = stats.overall_win_percentage()
        average_guesses = stats.average_guesses_per_win()

        embed = discord.Embed(title="Wordle Stats", colour=discord.Colour.blue())

        embed.add_field(name="Games played", value=stats.total_games, inline=True)
        embed.add_field(name="Wins", value=f"{stats.total_wins} ({percentage_wins:.2f}%)", inline=True)
        embed.add_field(name="\t Number of guesses", value=stats.total_guesses, inline=True)
        embed.add_field(name="Average guesses", value=f"{average_guesses:.3f}", inline=True)
        embed.add_field(name="Current streak", value=stats.win_streak, inline=True)
        embed.add_field(name="Longest streak", value=stats.longest_win_streak, inline=True)
        embed.add_field(name="Fastest win", value=f"{timedelta_format(stats.fastest_win)}", inline=True)

        # if wins are less than or equal than 0, there is no reason to show the rest, it also breaks the math
        if stats.total_wins <= 0:
            return embed

        embed.add_field(name="", value="", inline=False)

        embed = self.add_guess_hist(embed, stats)

        return embed
    
    def add_guess_hist(self, embed: discord.Embed, stats: WordleStats) -> discord.Embed:
        highest_guess_count = max(stats.guess_distribution.values())
        highest_guess_percentage = (highest_guess_count / stats.total_wins) * 100

        sorted_guess_distribution = sorted(stats.guess_distribution.items(), key=lambda key: int(key[0]))
        for guess_amount, guess_count in sorted_guess_distribution:
            if guess_count == 0:
                continue
            percentage = (guess_count / stats.total_wins) * 100
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
        formatted_known_letters = f"Known letters:\n{" ".join(sorted_known_letters)}"
        formatted_unknown_letters = f"Available letters:\n{" ".join(sorted_available_letters)}"
        return f"{formatted_known_letters}\n{formatted_unknown_letters}"

    @staticmethod
    def format_word(result: List[int]) -> str:
        result_map = {0: ":red_square:", 1:":yellow_square:", 2:":green_square:"}
        return " ".join([result_map[result] for result in result])

    @staticmethod
    def make_game_over_embed(daily_word: str) -> discord.Embed:
        """Create the embed for when no one guessed the word"""
        description = f"The word was **[{daily_word}](https://www.merriam-webster.com/dictionary/{daily_word})**"

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
    

class WordleFinishedController(discord.ui.View):
    def __init__(self, game: WordleGame, view: WordleView):
        self.game: WordleGame = game
        self.view: WordleView = view
        super().__init__(timeout=10*60)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        prev_game = await WordleGame.get_previous_game(self.game)
        if prev_game is None:
            await interaction.response.defer()
            return
        embed = await self.view.make_wordle_embed(prev_game)
        await interaction.response.edit_message(
            embed=embed, 
            view=WordleFinishedController(prev_game, self.view)
        )

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        next_game = await WordleGame.get_next_game(self.game)
        if next_game is None:
            await interaction.response.defer()
            return

        embed = await self.view.make_wordle_embed(next_game)
        await interaction.response.edit_message(
            embed=embed, 
            view=WordleFinishedController(next_game, self.view)
        )
        