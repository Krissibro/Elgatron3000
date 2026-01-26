import string

import discord

from typing import List, Set, Iterable, Tuple

from app.commands.wordle.wordle_db import WordleDB
from app.core.elgatron import Elgatron

from app.models import WordleGame, WordleGuess
from app.utilities.validators import validate_messageable
from app.utilities.helper_functions import timedelta_format
from app.commands.wordle.wordle_logic import wordle_logic

class WordleView:
    def __init__(self, bot: Elgatron, wordle_model: WordleDB):
        self.bot: Elgatron = bot
        self.wordle_db: WordleDB = wordle_model

        self.channel_id = bot.testing_channel_id if bot.testing else bot.wordle_channel_id

    async def make_wordle_embed(self) -> discord.Embed:
        game = await self.wordle_db.get_current_game()

        if game.finished:
            embed = discord.Embed(title=f"Congratulations!", color=discord.Color.green(),
                                  description=f"The word was **[{game.word.upper()}](https://www.merriam-webster.com/dictionary/{game.word})**!")
            if game.final_guess_time is not None and game.first_guess_time is not None:
                time_taken =  game.final_guess_time - game.first_guess_time
                embed.add_field(name=f"Time spent:   ",
                                value=f"{timedelta_format(time_taken)}", inline=False)

            embed.add_field(name="", value="", inline=False)
        else:
            embed = discord.Embed(title="Daily Wordle")

        if not any([True for _ in game.guesses]):
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

        separator = "\u00A0\u00A0\u00A0\u00A0"

        for guess in guesses:
            result = wordle_logic(guess.word, solution)

            # Track letters
            for letter, score in zip(guess.word, result):
                unknown_letters.discard(letter)
                if score:
                    known_letters.add(letter)

            # Build embed field
            formatted_word = separator.join(guess.word)
            fields.append((
                f" **{formatted_word}**     <-  {guess.guesser_name}",
                self.format_word(result)
            ))
        return fields, known_letters, unknown_letters

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