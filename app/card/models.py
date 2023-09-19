from uuid import uuid4

from enum import IntEnum
from game.models import Game
from model_base import Models
from pony.orm import PrimaryKey, Required, Set


class CardType(IntEnum):
    PANIC = 0
    STAY_AWAY = 1
    INFECTED = 2
    IT = 3


class Card(Models.Entity):
    id = PrimaryKey(int, auto=True)
    card_token = Required(str, unique=True, index=True, default=str(uuid4()))
    name = Required(str, unique=True, index=True)
    type = Required(CardType)
    game = Set("Game")  # Define the reverse attribute as "cards"
