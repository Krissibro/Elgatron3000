import discord
import os
import json

from utilities.helper_functions import format_millisecond_duration


class WordleStats:
    stats_file_path = "data/wordle_stats.json"

    games_played = 0
    wins = 0
    correct_guess_streak = 0
    longest_guess_streak = 0
    number_of_guesses = 0
    # In milliseconds
    fastest_win = 0
    number_guesses_per_game_counter = {}

    def __init__(self):
        self.load_stats()

    def increment_games_played(self):
        self.games_played += 1
        self.save_stats()

    def handle_win(self, guesses, reset_time, correct_guess_time):
        self.wins += 1
        self.correct_guess_streak += 1
        self.longest_guess_streak = max(self.longest_guess_streak, self.correct_guess_streak)
        self.number_of_guesses += guesses

        time_difference = correct_guess_time - reset_time
        total_milliseconds = int(time_difference.total_seconds() * 1000)
        self.fastest_win = min(self.fastest_win, total_milliseconds) if self.fastest_win > 0 else total_milliseconds

        self.number_guesses_per_game_counter[str(guesses)] = self.number_guesses_per_game_counter.get(str(guesses), 0) + 1
        self.number_guesses_per_game_counter = {
            key: self.number_guesses_per_game_counter[key]
            for key in sorted(self.number_guesses_per_game_counter, key=lambda key: int(key))
        }

        self.save_stats()

    def reset_streak(self):
        self.correct_guess_streak = 0
        self.save_stats()

    async def make_embed(self):
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
        embed.add_field(name="Current streak", value=self.correct_guess_streak, inline=True)
        embed.add_field(name="Longest streak", value=self.longest_guess_streak, inline=True)

        if self.fastest_win > 0:
            embed.add_field(name="Fastest win", value=f"{format_millisecond_duration(self.fastest_win)}", inline=True)

        # if wins are less than or equal than 0, there is no reason to show the rest, it also breaks the math
        if self.wins <= 0:
            return embed

        embed.add_field(name="\u200b", value="", inline=False)

        highest_guess_count = max(self.number_guesses_per_game_counter.values())
        highest_guess_percentage = (highest_guess_count / self.wins) * 100

        for guess_amount, guess_count in self.number_guesses_per_game_counter.items():
            if guess_count == 0:
                continue
            percentage = (guess_count / self.wins) * 100
            # Scale percentage to fit in max 15 squares per line, 15 is max that can fit on mobile
            square_count = int(percentage / highest_guess_percentage * 15 + 0.5)

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
            "correct_guess_streak": self.correct_guess_streak,
            "longest_guess_streak": self.longest_guess_streak,
            "number_of_guesses": self.number_of_guesses,
            "fastest_win": self.fastest_win,
            "number_guesses_per_game_counter": self.number_guesses_per_game_counter
        }

    def retrieve_data_from_dict(self, data):
        """Load the state from a dictionary."""
        self.games_played = data.get("number_of_games_played", 0)
        self.wins = data.get("number_of_correct_guesses", 0)
        self.correct_guess_streak = data.get("correct_guess_streak", 0)
        self.longest_guess_streak = data.get("longest_guess_streak", 0)
        self.number_of_guesses = data.get("number_of_guesses", 0)
        self.fastest_win = data.get("fastest_win", 0)
        self.number_guesses_per_game_counter = data.get("number_guesses_per_game_counter", {})

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
        else:
            self.save_stats()
