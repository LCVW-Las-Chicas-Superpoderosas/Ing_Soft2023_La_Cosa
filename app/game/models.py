from datetime import datetime
from enum import IntEnum

from model_base import Models
from pony.orm import Optional, PrimaryKey, Required, Set
import json


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
    turns = Optional(str, nullable=True)  # Store turns as a JSON string

    def get_turns(self):
        # Convert the JSON list into a python list
        return json.loads(self.turns) if self.turns else []

    def set_turns(self):
        turns_list = []

        for player in self.players:
            if not player.is_in_game(self.id):
                raise ValueError('Player must be in the game.')
            elif not player.is_alive:
                continue
            turns_list.append(player.id)

        # Convert the List to JSON List
        json_list = json.dumps(turns_list)
        self.turns = json_list

    def next_turn(self):
        # The first turn goes to the last position and the second turn goes first
        turns_list = self.get_turns()
        turns_list.append(turns_list.pop(0))

        # Convert the List to JSON List
        json_list = json.dumps(turns_list)
        self.turns = json_list
