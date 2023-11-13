import random

from model_base import ModelBase
from player.models import Player
from pony.orm import db_session

MODEL_BASE = ModelBase()

# status codes for the effects
FAIL = 0
SUCCESS = 1
BEING_PLAYED = 2


def flame_torch(target_id):
    try:
        with db_session:
            target_user = MODEL_BASE.get_first_record_by_value(Player, id=target_id)
            target_user.is_alive = False
            target_user.flush()
            return {
                'status': SUCCESS
            }
    except Exception as e:
        print(e)
        return {
            'status': FAIL
        }


# "watch_your_back" is a card that sets Game.clockwise to False
def watch_your_back(player_id):
    try:
        with db_session:
            player = MODEL_BASE.get_first_record_by_value(Player, id=player_id)
            game = player.game
            game.clockwise = not game.clockwise
            game.flush()
            return {
                'status': SUCCESS
            }
    except Exception as e:
        print(e)
        return {
            'status': FAIL
        }


def swap_places(target_id):
    try:
        with db_session:

            # get target
            target = MODEL_BASE.get_first_record_by_value(Player, id=target_id)

            # get game
            game = target.game

            # get player who played the swap
            player_turn = game.current_turn
            player = MODEL_BASE.get_first_record_by_value(Player, my_position=player_turn)

            # swap
            target_position = target.my_position
            target.my_position = player.my_position
            player.my_position = target_position

            # set the current_turn to the player that played the car
            # so it can finish the turn
            game.current_turn = player.my_position

            target.flush()
            player.flush()
            game.flush()
            return {
                'status': SUCCESS
            }
    except Exception as e:
        print(e)
        return {
            'status': FAIL
        }


# "suspicion" retrieves a random card from the target player's hand
def suspicion(target_id):
    try:
        with db_session:
            target_user = MODEL_BASE.get_first_record_by_value(Player, id=target_id)
            # first get the Set of cards from the target player
            cards_set = target_user.cards
            # then get a random card from that Set
            random_card = random.choice(list(cards_set))

            # create a dict with status
            # and data the card name
            return {
                'status': SUCCESS,
                'data': random_card.card_token
            }

    except Exception as e:
        print(e)
        return {
            'status': FAIL
        }


def seduction(target_id):
    try:
        with db_session:
            target_user = MODEL_BASE.get_first_record_by_value(Player, id=target_id)
            # first get the Set of cards from the target player
            cards_set = target_user.cards
            # then get a random card from that Set
            random_card = random.choice(list(cards_set))

            # create a dict with status
            # and data the card name
            return {
                'status': SUCCESS,
                'data': random_card.card_token
            }

    except Exception as e:
        print(e)
        return {
            'status': FAIL
        }



def analysis(target_id):
    try:
        with db_session:
            target_user = MODEL_BASE.get_first_record_by_value(Player, id=target_id)

            all_card_tokens = {card.card_token for card in target_user.cards}  # devuelve un set de card_tokens

            return {
                'status': SUCCESS,
                'data': all_card_tokens
            }
    except Exception as e:

        print(e)
        return {
            'status': FAIL
        }

def im_good_here(player_id):
    try:
        with db_session:
            player = MODEL_BASE.get_first_record_by_value(Player, id=player_id)
            game = player.game
        
            no_stay_away_card = True

            while no_stay_away_card:
                next_card = game.next_card_in_deck()
                card_token = next_card.card_token
                card_token_id = int(card_token[3:-4])  # Extrae el numero del card token string
                if card_token_id <= 88 and card_token_id >= 0:
                    player.add_card(next_card)
                    no_stay_away_card = False
                    game.delete_first_card_in_deck()

                if card_token_id <= 108 and card_token_id >= 89:
                    game.add_card_to_discard_pile(next_card.id)
                    game.delete_first_card_in_deck()

            return {
                'status': SUCCESS,
            }
    except Exception as e:

        print(e)
        return {
            'status': FAIL
        }
    
def no_thanks(player_id):
    try:
        with db_session:
            player = MODEL_BASE.get_first_record_by_value(Player, id=player_id)
            game = player.game
        
            no_stay_away_card = True

            while no_stay_away_card:
                next_card = game.next_card_in_deck()
                card_token = next_card.card_token
                card_token_id = int(card_token[3:-4])  # Extrae el numero del card token string
                if card_token_id <= 88 and card_token_id >= 0:
                    player.add_card(next_card)
                    no_stay_away_card = False
                    game.delete_first_card_in_deck()

                if card_token_id <= 108 and card_token_id >= 89:
                    game.add_card_to_discard_pile(next_card.id)
                    game.delete_first_card_in_deck()

            return {
                'status': SUCCESS,
            }
    except Exception as e:

        print(e)
        return {
            'status': FAIL
        }


EFFECTS_TO_PLAYERS = {
    'lanzallamas': flame_torch,
    'vigila tus espaldas': watch_your_back,
    'cambio de lugar!': swap_places,
    'sospecha': suspicion,
    'seduccion': seduction,
    'analisis': analysis,
    'aqui estoy bien': im_good_here,
    'no, gracias': no_thanks
}
