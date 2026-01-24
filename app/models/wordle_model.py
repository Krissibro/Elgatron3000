from datetime import datetime
from tortoise.models import Model
from tortoise import fields

class WordleGame(Model):
    id:                 fields.Field[int]       = fields.IntField(primary_key=True)
    date:               fields.Field[datetime] = fields.DatetimeField(null=True)
    word:               fields.Field[str]       = fields.CharField(max_length=16)
    first_guess_time:   fields.Field[datetime]  = fields.DatetimeField(null=True)
    final_guess_time:   fields.Field[datetime]  = fields.DatetimeField(null=True)
    guesses:            fields.ReverseRelation["WordleGuess"]

    def __str__(self):
        return f"{self.date.strftime('%d/%m/%y')} - {self.word}"


class WordleGuess(Model):
    id:         fields.Field[int]                       = fields.IntField(primary_key=True)
    word:      fields.Field[str]                       = fields.CharField(max_length=16)
    guesser_id:    fields.Field[int]                       = fields.IntField()
    guesser_name:  fields.Field[str]                       = fields.CharField(max_length=64)
    time: fields.Field[datetime]                  = fields.DatetimeField(null=True)

    game:       fields.ForeignKeyRelation["WordleGame"]   = fields.ForeignKeyField(
        model_name="models.WordleGame",
        related_name="guesses",
        on_delete=fields.CASCADE
    )

    def __str__(self):
        return f"{self.guesser_name} - {self.word}"

    def is_correct(self) -> bool:
        return self.word == self.game.word
