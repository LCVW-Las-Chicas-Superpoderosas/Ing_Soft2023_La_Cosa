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
    deck = Optional(str, nullable=True) # Store deck as a JSON string
    graveyard = Optional(str, nullable=True) # Store graveyard(discarded cards) as a JSON string
    turns = Optional(str, nullable=True)  # Store turns as a JSON string

    def get_graveyard(self):
        # JSON list -> Python list
        return json.loads(self.graveyard) if self.graveyard else []

    def set_graveyard(self, new_discarded_card):

        graveyard_list = self.get_graveyard
        
        graveyard_list.append(new_discarded_card.id)
        
        # List -> Json List
        json_list = json.dumps(graveyard_list)
        self.graveyard = json_list

    def get_deck(self):
        # Convert the JSON list into a python list
        return json.loads(self.deck) if self.deck else []

    def set_deck(self, new_card_in_deck):
        # Get actual list
        deck_list = self.get_deck()
        # Inser new element
        deck_list.insert(new_card_in_deck.id)

        # Convert the List to JSON List
        json_list = json.dumps(deck_list)
        self.turns = json_list

    def next_card_in_deck(self):
        # JSON list to List and get first card.
        deck_list = self.get_deck()
        next_card_id = deck_list[0]
        deck_list.pop(0) # Falta ver si guardar en algun lado first_card

        # Retrieve the card in the set
        for card in self.cards:
            if card.id == next_card_id:
                next_card = card
                break

        # Convert the List to JSON List
        json_list = json.dumps(deck_list)
        self.turns = json_list

        return next_card
    
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
