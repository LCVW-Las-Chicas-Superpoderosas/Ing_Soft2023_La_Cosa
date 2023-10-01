from datetime import datetime

from game.models import Game
from model_base import Models
from pony.orm import PrimaryKey, Optional, Required, Set


class Player(Models.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    created_at = Required(datetime, default=datetime.utcnow)
    game = Optional(Game)
    cards = Set('Card')
    is_alive = Required(bool, default=True)

    def is_in_game(self, game_id):
        if self.game is None:
            return False
        return game_id == self.game.id
