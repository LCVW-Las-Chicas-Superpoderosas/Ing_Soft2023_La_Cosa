from game.models import Game
from card.models import CardType
from model_base import Models
from pony.orm import PrimaryKey, Optional, Required, Set


class Player(Models.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    game = Optional(Game)
    cards = Set('Card')
    is_alive = Required(bool, default=True)
    infected = Optional(bool, default=False)
    my_position = Optional(int)

    def is_in_game(self, game_id):
        if self.game is None:
            return False
        return game_id == self.game.id

    def leave_game(self):
        self.game = None

    def add_cards(self, cards):
        self.cards = cards

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
        card.delete()

    def check_card_in_hand(self, card_id):
        card = self.cards.select().filter(id=card_id).first()
        return card is not None

    def check_defense_of_card_attack_in_hand(self, attack_card_id):
        has_defense = False
        if attack_card_id >= 22 and attack_card_id <= 26:  # para lanzallamas
            for card in self.cards:
                if card.id <= 83 and card.id >= 81:  # para Nada de barbacoas!
                    has_defense = True

        if attack_card_id >= 50 and attack_card_id <= 59:  # para Cambio de lugar! y Mas vale que corras!
            for card in self.cards:
                if card.id >= 71 and card.id <= 73:  # para Aqui estoy bien!
                    has_defense = True
        return has_defense

    def check_defense_of_exchange_in_hand(self):
        has_defense = False
        for card in self.cards:
            if card.id >= 67 and card.id <= 70:  # para Aterrador
                has_defense = True
            if card.id >= 74 and card.id <= 80:  # para No, Gracias!  y  Fallaste!
                has_defense = True
        return has_defense

    def return_defense_cards_of_exchange(self):
        card_tokens = []
        for card in self.cards:
            if card.id >= 67 and card.id <= 70:  # para Aterrador
                card_tokens.append({
                    'card_tokens': card.card_token
                })
            if card.id >= 74 and card.id <= 80:  # para No, Gracias!  y  Fallaste!
                card_tokens.append({
                    'card_tokens': card.card_token
                })
        return card_tokens

    def return_defense_cards_of_attack(self, attack_card_id):
        card_tokens = []
        if attack_card_id >= 22 and attack_card_id <= 26:  # para lanzallamas
            for card in self.cards:
                if card.id <= 83 and card.id >= 81:  # para Nada de barbacoas!
                    card_tokens.append({
                        'card_tokens': card.card_token
                    })

        if attack_card_id >= 50 and attack_card_id <= 59:  # para Cambio de lugar! y Mas vale que corras!
            for card in self.cards:
                if card.id >= 71 and card.id <= 73:  # para Aqui estoy bien!
                    card_tokens.append({
                        'card_tokens': card.card_token
                    })
        return card_tokens
