from datetime import datetime

from game.models import Game
from card.models import CardType
from model_base import Models
from pony.orm import PrimaryKey, Optional, Required, Set


class Player(Models.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    created_at = Required(datetime, default=datetime.utcnow)
    game = Optional(Game)
    cards = Set('Card')
    is_alive = Required(bool, default=True)
    infected = Optional(bool, default=False)
    my_position = Optional(int)

    def is_in_game(self, game_id):
        if self.game is None:
            return False
        return game_id == self.game.id

    def add_cards(self, cards):
        self.cards = cards

    def is_infected(self):
        card = None
        if self.cards is not None:
            card = self.cards.get(type=CardType.INFECTED)
        return True if card else False

    def is_the_thing(self):
        card = None
        if self.cards is not None:
            card = self.cards.get(type=CardType.IT)
        return True if card else False
