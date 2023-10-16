from player.models import Player
from card.models import Card, CardType
from model_base import ModelBase
from game.models import Game
from chat.models import Chat
from pony.orm import commit, db_session

import re


@db_session
def populate_db_test():
    model_base = ModelBase()
    load_cards()
    player1 = model_base.add_record(Player, name='Gonzalo')
    player2 = model_base.add_record(Player, name='Juan')
    player3 = model_base.add_record(Player, name='Pedro')
    player4 = model_base.add_record(Player, name='Maria')
    model_base.add_record(Player, name='Lautaro')

    chat = model_base.add_record(Chat)
    # add set of players to game
    model_base.add_record(
        Game, name='Bahamas', players=[player1, player2, player3, player4],
        chats=chat, cards={},
        min_players=4, max_players=4, host=1)


def get_cards_from_text(text):
    result = []
    lines = text.split('\n')  # Split the text into lines
    pattern = r'(\d+)- (\s*[^\d:]+) (\d*) - (\d)'

    for line in lines:
        match = re.match(pattern, line)
        if match:
            card_id = match.group(1)
            card_name = match.group(2)
            card_number = match.group(3)
            card_type = match.group(4)
            result.append((card_id, card_name, card_type, card_number))
    return result


@db_session
def load_cards():
    model_base = ModelBase()
    with open('./app/statics/cards.txt', 'r') as f:
        cards_schema = f.read()

    cards = get_cards_from_text(cards_schema)

    for card in cards:
        model_base.add_record(Card, name=card[1],
            card_token=f'img{card[0]}.jpg', type=card[2], number=card[3])
        commit()
    model_base.add_record(Card, name='Reverse', number=None,
        card_token='reverse.jpg', type=CardType.OTHER.value)
    model_base.add_record(Card, name='Panic Reverse', number=None,
        card_token='panic-reverse.jpg', type=CardType.OTHER.value)
    print('Cards loaded successfully')
