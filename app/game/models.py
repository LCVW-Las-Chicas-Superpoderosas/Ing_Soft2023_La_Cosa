from datetime import datetime

from model_base import Models
from pony.orm import Optional, PrimaryKey, Required, Set


class Game(Models.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    password = Optional(str, nullable=True)
    created_at = Required(datetime, default=datetime.utcnow)
    host = Required(int)  # Player_id of the host
    chats = Required('Chat')
    cards = Set('Card', nullable=True)
    players = Set('Player')
    min_players = Required(int)
    max_players = Required(int)
