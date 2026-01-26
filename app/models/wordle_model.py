from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from tortoise import fields
from tortoise.models import Model


class WordleGame(Model):
    id:                 int                 = fields.IntField(primary_key=True)     # type: ignore[assignment]

    game_date:          Optional[date]      = fields.DateField(null=True)           # type: ignore[assignment]
    word:               str                 = fields.CharField(max_length=16)       # type: ignore[assignment]
    first_guess_time:   Optional[datetime]  = fields.DatetimeField(null=True)       # type: ignore[assignment]
    final_guess_time:   Optional[datetime]  = fields.DatetimeField(null=True)       # type: ignore[assignment]
    finished:           bool                = fields.BooleanField(default=False)    # type: ignore[assignment]

    guesses: fields.ReverseRelation[WordleGuess]


class WordleGuess(Model):
    id:             int                 = fields.IntField(primary_key=True) # type: ignore[assignment]

    word:           str                 = fields.CharField(max_length=16)   # type: ignore[assignment]
    guesser_id:     int                 = fields.IntField()                 # type: ignore[assignment]
    guesser_name:   str                 = fields.CharField(max_length=64)   # type: ignore[assignment]
    time:           Optional[datetime]  = fields.DatetimeField(null=True)   # type: ignore[assignment]

    game: fields.ForeignKeyRelation[WordleGame] = fields.ForeignKeyField(
        model_name="models.WordleGame",
        related_name="guesses",
        on_delete=fields.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.guesser_name} - {self.word}"

    def is_correct(self) -> bool:
        return self.word == self.game.word