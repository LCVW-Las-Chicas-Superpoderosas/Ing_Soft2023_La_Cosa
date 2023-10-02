from game.models import Game
from card.models import Card, CardType
from player.models import Player
from pony.orm import Database, db_session, select, JOIN
from constants import DATABASE_URL, MYSQL_PASS, MYSQL_USER
from model_base import ModelBase, initialize_database
from random import shuffle


model_base = ModelBase()

def get_card_by_cardid(game:Game, card_id):
    for card in game.cards:
        if card.id == card_id:
            return card
    return None # Should never Happen

def get_card_by_card_type(game:Game, card_type):
    for card in game.cards:
        if card.type == card_type:
            return card

def get_card_by_cardid(game:Game, card_id):
    for card in game.cards:
        if card.id == card_id:
            return card
    return None # Should never Happen


def assign_cards_to_game_and_6players_hardcoded_deck(game: Game):
    amount_of_players = 6

    with db_session:
        game_cards = model_base.get_records_by_value(Card, lambda card: card.number <= amount_of_players)
        game.cards = {card for card in game_cards}
        for card in game.cards:
            game.set_deck(card)

        deck = game.get_deck()
        for player in game.players:
            player.cards.add(get_card_by_cardid(deck[0]))
            player.cards.add(get_card_by_cardid(deck[1]))
            player.cards.add(get_card_by_cardid(deck[2]))
            player.cards.add(get_card_by_cardid(deck[3]))

def assign_cards_to_game(game: Game):

    initialize_database()

    amount_of_players = len(game.players)

    with db_session:
        game_cards: set[Card] = model_base.get_records_by_value(Card, lambda card: card.number <= amount_of_players)
        game.cards = {card for card in game_cards}

def initial_repartition_to_players(game: Game):

    # Asumes assign_cards_to_game was done.
    all_cards_id = {card.id for card in game.cards}# Aux
    la_cosa_card_id = get_card_by_card_type(game, 0).id

    # Sirve para la reparticion inicial
    initial_repartition_amount = len(game.players)*4 - 1
    mazoMezclaInicial = [card.id for card in game.cards if card.type not in {0,2}][:initial_repartition_amount]
    shuffle(mazoMezclaInicial)
    mazoMezclaInicial.add(la_cosa_card_id)
    shuffle(mazoMezclaInicial)
    # Esto sirve luego para armar el deck restante
    cartas_a_un_lado1 = [card.id for card in game.cards if card.type == 2] ## Las cartas de infectado
    cartas_a_un_lado2 = [x for x in all_cards_id if x not in mazoMezclaInicial
                          and x not in cartas_a_un_lado1 
                          and x.type != 0] # Cartas que sobraron de las type==1

    ## Completar

