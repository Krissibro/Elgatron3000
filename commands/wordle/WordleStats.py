from collections import defaultdict
from datetime import timedelta
import discord
import os
import json

from utilities.helper_functions import timedelta_format


class WordleStats:
    def __init__(self):
        self.games_played: int = 0
        self.wins: int = 0
        self.win_streak: int = 0
        self.longest_win_streak: int = 0
        self.number_of_guesses: int = 0

        self.fastest_win: timedelta = timedelta(seconds=0)
        self.guess_distribution = defaultdict(int)

        self.stats_file_path: str = "data/wordle_stats.json"
        self.load_stats()

    def increment_games_played(self):
        self.games_played += 1
        self.save_stats()

    def handle_win(self, guesses, time_taken):
        self.wins += 1
        self.win_streak += 1
        self.longest_win_streak = max(self.longest_win_streak, self.win_streak)
        self.number_of_guesses += guesses

        if self.fastest_win.total_seconds() == 0:
            # First win
            self.fastest_win = time_taken
        else:
            self.fastest_win = min(self.fastest_win, time_taken)

        self.guess_distribution[str(guesses)] += 1

        self.save_stats()

    def reset_streak(self):
        self.win_streak = 0
        self.save_stats()

    def make_embed(self):
        percentage_wins = (
            f"{(self.wins / self.games_played * 100):.2f}"
            if self.games_played > 0 else "0.00"
        )
        average_guesses = (self.number_of_guesses / self.wins) if self.games_played > 0 and self.wins > 0 else 0

        embed = discord.Embed(title="Wordle Stats", colour=discord.Colour.blue())
        embed.add_field(name="Games played", value=self.games_played, inline=True)
        embed.add_field(name="Wins", value=f"{self.wins} \u00A0\u00A0\u00A0 ({percentage_wins}%)", inline=True)
        embed.add_field(name="\t Number of guesses", value=self.number_of_guesses, inline=True)
        embed.add_field(name="Average guesses", value=f"{average_guesses:.3f}", inline=True)
        embed.add_field(name="Current streak", value=self.win_streak, inline=True)
        embed.add_field(name="Longest streak", value=self.longest_win_streak, inline=True)

        if self.fastest_win.total_seconds() > 0:
            embed.add_field(name="Fastest win", value=f"{timedelta_format(self.fastest_win)}", inline=True)

        # if wins are less than or equal than 0, there is no reason to show the rest, it also breaks the math
        if self.wins <= 0:
            return embed

        embed.add_field(name="\u200b", value="", inline=False)

        embed = self.add_guess_hist(embed)

        return embed

    def add_guess_hist(self, embed: discord.Embed) -> discord.Embed:
        highest_guess_count = max(self.guess_distribution.values())
        highest_guess_percentage = (highest_guess_count / self.wins) * 100

        sorted_guess_distribution = sorted(self.guess_distribution.items(), key=lambda key: int(key[0]))
        for guess_amount, guess_count in sorted_guess_distribution:
            if guess_count == 0:
                continue
            percentage = (guess_count / self.wins) * 100
            # Scale percentage to fit in max 14 squares per line, 14 is max that can fit on mobile
            square_count = int(percentage / highest_guess_percentage * 14 + 0.5)

            embed.add_field(
                name=f"{guess_amount} guesses:      {guess_count}   ({percentage:.2f}%)",
                value=square_count * ":blue_square:" if square_count > 0 else ":black_large_square:",
                inline=False
            )
        return embed

    def get_dict_of_data(self):
        """Convert the current state to a dictionary."""
        return {
            "number_of_games_played": self.games_played,
            "number_of_correct_guesses": self.wins,
            "win_streak": self.win_streak,
            "longest_win_streak": self.longest_win_streak,
            "number_of_guesses": self.number_of_guesses,
            "fastest_win": self.fastest_win.seconds*1000 + self.fastest_win.microseconds//1000,
            "guess_distribution": dict(self.guess_distribution)
        }

    def retrieve_data_from_dict(self, data):
        """Load the state from a dictionary."""
        self.games_played = data.get("number_of_games_played", 0)
        self.wins = data.get("number_of_correct_guesses", 0)
        self.win_streak = data.get("correct_guess_streak", 0)
        self.longest_win_streak = data.get("longest_guess_streak", 0)
        self.number_of_guesses = data.get("number_of_guesses", 0)

        fastest_win_data = data.get("fastest_win", 0)
        self.fastest_win = timedelta(milliseconds=fastest_win_data)

        self.guess_distribution = defaultdict(int, data.get("guess_distribution", {}))

    def save_stats(self):
        """Save the current state to a JSON file."""
        with open(self.stats_file_path, 'w') as file:
            json.dump(self.get_dict_of_data(), file)

    def load_stats(self):
        """Load the state from a JSON file if it exists."""
        if os.path.exists(self.stats_file_path):
            with open(self.stats_file_path, 'r') as file:
                stats_dict = json.load(file)
                self.retrieve_data_from_dict(stats_dict)
