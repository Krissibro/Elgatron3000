from datetime import date, datetime, timedelta
from typing import Optional

from tortoise import fields
from tortoise.models import Model


class WordleGame(Model):
    id: int = fields.IntField(primary_key=True)  # ty:ignore[invalid-assignment]

    game_date: date | None = fields.DateField(null=True)  # ty:ignore[invalid-assignment]
    word: str = fields.CharField(max_length=16)  # ty:ignore[invalid-assignment]

    guesses: fields.ReverseRelation["WordleGuess"]

    async def get_previous_game(self) -> Optional["WordleGame"]:
        """Get the game before the given game."""
        previous_game = (
            await self.__class__.filter(id__lt=self.id)
            .prefetch_related("guesses")
            .last()
        )
        return previous_game

    async def get_next_game(self) -> Optional["WordleGame"]:
        """Get the game after the given game."""
        next_game = (
            await self.__class__.filter(id__gt=self.id)
            .prefetch_related("guesses")
            .first()
        )
        return next_game

    def is_finished(self) -> bool:
        """Check if the game is finished."""
        return any(guess.word == self.word for guess in self.guesses)

    def time_taken(self) -> timedelta | None:
        """measure time between first and latest guess, or None if not guesses is undefined or empty"""
        # make sure guesses are already prefetched
        if not self.guesses:
            return None

        guesses_sorted = sorted(self.guesses, key=lambda g: g.time)
        first_guess = guesses_sorted[0]
        last_guess = guesses_sorted[-1]
        return last_guess.time - first_guess.time

    def guess_count(self) -> int:
        """Return the number of guesses made in this game."""
        return len(self.guesses)


class WordleGuess(Model):
    id: int = fields.IntField(primary_key=True)  # ty:ignore[invalid-assignment]

    word: str = fields.CharField(max_length=16)  # ty:ignore[invalid-assignment]
    guesser_name: str = fields.CharField(max_length=64)  # ty:ignore[invalid-assignment]
    guesser_id: str = fields.CharField(max_length=64)  # ty:ignore[invalid-assignment]

    time: datetime = fields.DatetimeField(null=False)  # ty:ignore[invalid-assignment]
    game: WordleGame = fields.ForeignKeyField(  # ty:ignore[invalid-assignment]
        "models.WordleGame",
        related_name="guesses",
        on_delete=fields.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.guesser_name} - {self.word}"


class WordleStats(Model):
    id: int = fields.IntField(primary_key=True)  # ty:ignore[invalid-assignment]
    server_id: int = fields.IntField(unique=True)  # ty:ignore[invalid-assignment]

    total_games: int = fields.IntField(default=0)  # ty:ignore[invalid-assignment]
    total_wins: int = fields.IntField(default=0)  # ty:ignore[invalid-assignment]
    total_guesses: int = fields.IntField(default=0)  # ty:ignore[invalid-assignment]

    win_streak: int = fields.IntField(default=0)  # ty:ignore[invalid-assignment]
    longest_win_streak: int = fields.IntField(default=0)  # ty:ignore[invalid-assignment]
    fastest_win: timedelta = fields.TimeDeltaField(  # ty:ignore[invalid-assignment]
        default=timedelta(hours=23, minutes=59, seconds=59)
    )

    guess_distribution: dict = fields.JSONField(  # ty:ignore[invalid-assignment]
        default=dict
    )

    def overall_win_percentage(self) -> float:
        if self.total_games == 0:
            return 0.0
        return (self.total_wins / self.total_games) * 100

    def average_guesses_per_win(self) -> float:
        if self.total_wins == 0:
            return 0.0
        return self.total_guesses / self.total_wins
