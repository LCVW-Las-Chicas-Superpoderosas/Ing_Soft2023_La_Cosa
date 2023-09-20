from game.models import Game
from model_base import Models
from pony.orm import PrimaryKey, Optional


class Chat(Models.Entity):
    id = PrimaryKey(int, auto=True)
    game = Optional("Game")
