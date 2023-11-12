from game.models import Game
from card.models import CardType
from model_base import Models
from pony.orm import PrimaryKey, Optional, Required, Set


DEFENSE_EFFECTS = {
    'lanzallamas': ['Nada de barbacoas!']
    # add more when u need to do your tickets
}


class Player(Models.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    game = Optional(Game)
    cards = Set('Card')
    is_alive = Required(bool, default=True)
    infected = Optional(bool, default=False)
    my_position = Optional(int)
    last_card_token_played = Optional(str)

    def is_in_game(self, game_id):
        if self.game is None:
            return False
        return game_id == self.game.id

    def leave_game(self):
        self.game = None

    def add_cards(self, cards):
        self.cards = cards

    def add_card(self, card):
        card_list = list(self.cards)
        card_list.append(card)
        self.cards = card_list

    def can_neglect_exchange(self):
        defense_cards = ['Fallaste!', 'Aterrador', '¡No, gracias!']
        cards = []
        for name in defense_cards:
            c = self.cards.select().filter(name=name).first()
            if c is not None:
                cards.append(c.card_token)
        return cards

    def can_defend(self, card_name):
        cards = []
        for name in DEFENSE_EFFECTS[card_name.lower()]:
            c = self.cards.select().filter(name=name).first()
            if c is not None:
                cards.append(c.card_token)
        return cards

    def get_hand(self):
        return [
            {'card_token': card.card_token, 'type': card.type}
            for card in self.cards
        ]

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

    def remove_card(self, card_id):
        card = self.cards.select().filter(id=card_id).first()
        card_list = list(self.cards)
        card_list.remove(card)

    def check_card_in_hand(self, card_id):
        card = self.cards.select().filter(id=card_id).first()
        return card is not None

    def check_card_token_in_hand(self, card_token):
        card = self.cards.select().filter(card_token=card_token).first()
        return card is not None
