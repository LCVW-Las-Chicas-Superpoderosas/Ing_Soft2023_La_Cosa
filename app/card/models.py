from uuid import uuid4

from enum import IntEnum
from model_base import Models
from pony.orm import Optional, PrimaryKey, Required, Set


EXCHANGE_CARDS = ['seduccion']


class CardType(IntEnum):
    OTHER = -1
    PANIC = 0
    STAY_AWAY = 1
    INFECTED = 2
    IT = 3


class Card(Models.Entity):
    id = PrimaryKey(int, auto=True)
    card_token = Required(str, unique=True, index=True, default=str(uuid4()))
    name = Required(str)
    type = Required(CardType)
    game = Set('Game')  # Define the reverse attribute as "cards"
    player = Set('Player')  # Define the reverse attribute as "cards"
    number = Optional(int)  # Number 0 is only for IT card, Null is for not playable cards

    def is_exchange(self):
        return self.name.lower() in EXCHANGE_CARDS
