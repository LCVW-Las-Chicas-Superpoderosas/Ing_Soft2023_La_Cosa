import random
from datetime import datetime
from enum import IntEnum

from model_base import Models, ModelBase
from card.models import Card
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
    the_thing = Optional(int, nullable=True)  # Player_id of the thing
    chats = Required('Chat')
    cards = Set('Card', nullable=True, lazy=True)
    players = Set('Player')
    min_players = Required(int)
    max_players = Required(int)
    actual_turn = Optional(int)

    def get_turns(self):
        # Convert the JSON list into a python list
        return self.actual_turn

    def set_turns(self):
        total_players = len(self.players)
        turns = [random.randint(0, total_players - 1) for _ in range(
            total_players)]

        for player in self.players:
            if not player.is_alive:
                continue
            player.my_position = turns.pop(0)

        self.actual_turn = random.randint(0, total_players - 1)
        return self.actual_turn

    def next_turn(self):
        self.actual_turn += 1
        return self.actual_turn

    def check_turn(self, user_position):
        return user_position == self.get_turns()

    def validate_the_thing_win(self):
        # count alive players in the game with a list comprehension
        alive_players = self.players.filter(is_alive=True, infected=False)
        if alive_players.count() == 1 and alive_players.first().id == self.the_thing:
            self.status = GameStatus.FINISHED.value
            return True
        return False

    def validate_humans_win(self):
        # Check if all but one player are dead
        # count alive players in the game with a list comprehension
        it_player = self.players.filter(id=self.the_thing).first()

        if it_player is None:
            raise ValueError('The thing player not found in the game.')

        if not it_player.is_alive:
            self.status = GameStatus.FINISHED.value
            return True
        return False

    def give_cards_to_users(self):
        player_it = random.randint(0, len(self.players) - 1)
        self.the_thing = player_it

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
                torch = ModelBase().get_first_record_by_value(Card,
                    name='Lanzallamas', number=self.max_players)
                if torch is not None:
                    cards[1] = torch
            except Exception:
                pass

            player.add_cards(cards)

    def clean_game(self):
        self.players = []
        self.cards = []
        self.chat = None
