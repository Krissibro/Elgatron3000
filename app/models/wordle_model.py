from __future__ import annotations

from datetime import datetime, date, timedelta
from email.policy import default
from typing import Optional

from tortoise import fields
from tortoise.models import Model


class WordleGame(Model):
    id:                 int                 = fields.IntField(primary_key=True)     # type: ignore[assignment]

    game_date:          Optional[date]      = fields.DateField(null=True)           # type: ignore[assignment]
    word:               str                 = fields.CharField(max_length=16)       # type: ignore[assignment]

    guesses: fields.ReverseRelation[WordleGuess]

    async def get_previous_game(self) -> Optional["WordleGame"]:
        """Get the game before the given game."""
        previous_game = (
            await self.__class__
            .filter(id__lt=self.id)
            .prefetch_related("guesses")
            .last()
        )
        return previous_game

    async def get_next_game(self) -> Optional["WordleGame"]:
        """Get the game after the given game."""
        next_game = (
            await self.__class__
            .filter(id__gt=self.id)
            .prefetch_related("guesses")
            .first()
        )
        return next_game

    def is_finished(self) -> bool:
        """Check if the game is finished."""
        return any([guess.word == self.word for guess in self.guesses])
    
    def time_taken(self) -> Optional[timedelta]:
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
    id:             int                 = fields.IntField(primary_key=True) # type: ignore[assignment]

    word:           str                 = fields.CharField(max_length=16)   # type: ignore[assignment]
    guesser_id:     int                 = fields.IntField()                 # type: ignore[assignment]
    guesser_name:   str                 = fields.CharField(max_length=64)   # type: ignore[assignment]
    time:           datetime            = fields.DatetimeField(null=False)   # type: ignore[assignment]

    game: fields.ForeignKeyRelation[WordleGame] = fields.ForeignKeyField(
        model_name="models.WordleGame",
        related_name="guesses",
        on_delete=fields.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.guesser_name} - {self.word}"
    
class WordleStats(Model):
    id:                 int             = fields.IntField(primary_key=True) # type: ignore[assignment]
    server_id:          int             = fields.IntField(unique=True)      # type: ignore[assignment]

    total_games:        int             = fields.IntField(default=0)        # type: ignore[assignment]
    total_wins:         int             = fields.IntField(default=0)        # type: ignore[assignment]
    total_guesses:      int             = fields.IntField(default=0)        # type: ignore[assignment]

    win_streak:         int             = fields.IntField(default=0)        # type: ignore[assignment]
    longest_win_streak: int             = fields.IntField(default=0)        # type: ignore[assignment]
    fastest_win:        timedelta       = fields.TimeDeltaField(default=timedelta(hours=23, minutes=59, seconds=59))    # type: ignore[assignment]

    guess_distribution: dict            = fields.JSONField(default=dict)  # type: ignore[assignment]


    def overall_win_percentage(self) -> float:
        if self.total_games == 0:
            return 0.0
        return (self.total_wins / self.total_games) * 100
    
    def average_guesses_per_win(self) -> float:
        if self.total_wins == 0:
            return 0.0
        return self.total_guesses / self.total_wins