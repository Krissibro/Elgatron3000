from collections import defaultdict
from datetime import timedelta
import os
import json

class WordleStats:
    def __init__(self):
        self.games_played: int = 0
        self.wins: int = 0
        self.win_streak: int = 0
        self.longest_win_streak: int = 0
        self.number_of_guesses: int = 0

        self.fastest_win: timedelta = timedelta(seconds=0)
        self.guess_distribution = defaultdict(int)

        self.stats_file_path: str = "static/wordle_stats.json"
        self.load_stats()

    def increment_games_played(self):
        self.games_played += 1
        self.save_stats()

    def handle_win(self, guesses: int, time_taken: timedelta):
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
        self.win_streak = data.get("win_streak", 0)
        self.longest_win_streak = data.get("longest_win_streak", 0)
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
