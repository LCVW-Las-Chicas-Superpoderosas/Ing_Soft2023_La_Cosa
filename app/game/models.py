from datetime import datetime
from enum import IntEnum

from model_base import Models
from pony.orm import Optional, PrimaryKey, Required, Set


class GameStatus(IntEnum):
    WAITING = 0
    STARTED = 1
    FINISHED = 2


class Game(Models.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    status = Required(GameStatus, default=GameStatus.WAITING.value)
    password = Optional(str, nullable=True)
    created_at = Required(datetime, default=datetime.utcnow)
    host = Required(int)  # Player_id of the host
    chats = Required('Chat')
    cards = Set('Card', nullable=True)
    players = Set('Player')
    min_players = Required(int)
    max_players = Required(int)
