import json
import random
from datetime import datetime
from enum import IntEnum

from model_base import Models, ModelBase
from card.models import Card, CardType
from pony.orm import Optional, PrimaryKey, Required, Set


CARDS_PER_PERSON = 4


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
    cards = Set('Card', nullable=True, lazy=True)
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

        # Shuffle the list
        random.shuffle(turns_list)

        # Get host position and put it last
        host_position = turns_list.index(self.host)
        turns_list.append(turns_list.pop(host_position))

        # Convert the List to JSON List
        json_list = json.dumps(turns_list)
        self.turns = json_list

    def next_turn(self):
        # The first turn goes to the last position and the second turn goes
        # first
        turns_list = self.get_turns()
        turns_list.append(turns_list.pop(0))

        # Convert the List to JSON List
        json_list = json.dumps(turns_list)
        self.turns = json_list

    def is_game_over(self):
        # Check if all but one player are dead
        # count alive players in the game with a list comprehension
        alive_players = self.players.filter(is_alive=True).count()
        return alive_players <= 1
        
    def give_cards_to_users(self):
        player_it = random.randint(0, len(self.players) - 1)

        # We gonna give cards to each player 4 cards then 4 cards...
        # dont have time to think about a better approach.
        # i'm gonna upgrade the algorithm of this function later

        for i, player in enumerate(self.players):
            cards = self.cards.random(CARDS_PER_PERSON)
            if i == player_it:
                cards = list(cards)
                cards[0] = self.cards.select(number=0).first()

            self.cards.remove(cards)

            # This is needed bcs QueryResults are buggy and not documented...
            # https://github.com/ponyorm/pony/issues/369
            cards = list(cards)

            # Remove this after demo
            try:
                cards[1] = ModelBase().get_first_record_by_value(Card,
                    name='Lanzallamas', number=self.max_players)
            except Exception:
                pass

            player.add_cards(cards)
