from datetime import datetime

from model_base import Models
from pony.orm import PrimaryKey, Required, Set, Optional


class Game(Models.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    password = Optional(
        str, nullable=True
    )  # Define password as an optional (nullable) string field
    created_at = Required(datetime, default=datetime.utcnow)
    host = Required(int)  # Player_id of the host
    chats = Required('Chat')
    cards = Set('Card', nullable=True)
    players = Set('Player')
    min_players = Required(int)
    max_players = Required(int)
