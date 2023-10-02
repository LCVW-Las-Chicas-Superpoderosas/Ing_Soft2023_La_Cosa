from game.models import Game
from card.models import Card, CardType
from player.models import Player
from pony.orm import Database, db_session, select, JOIN
from constants import DATABASE_URL, MYSQL_PASS, MYSQL_USER
from model_base import ModelBase, initialize_database


model_base = ModelBase()


def assign_cards_to_game(game: Game):

    initialize_database()

    amount_of_players = len(game.players)

    with db_session:
        game_cards: Card = model_base.get_records_by_value(Card, lambda card: card.number <= amount_of_players)
        game.cards = {card for card in game_cards}

def initial_repartition_to_players(game: Game):
    # Asumes assign_cards_to_game was done.

    initial_repartition_amount = len(game.players)*4 - 1
    ## Completar

