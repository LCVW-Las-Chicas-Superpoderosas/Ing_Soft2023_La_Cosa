from card.models import Card, CardType
from chat.models import Chat
from game.models import Game
from model_base import ModelBase
from player.models import Player
from pony.orm import commit
import json


model_base = ModelBase()


def create_data_test():
    card = model_base.add_record(Card, name='test_card',
        card_token='test_card', type=CardType.PANIC.value)
    chat = model_base.add_record(Chat)
    player = model_base.add_record(Player, name='test', cards=card)
    game = model_base.add_record(Game, name='test', password='', chats=chat,
            cards=card, players=player, host=1, min_players=4, max_players=8,
            turns=json.dumps([player.id]))
    commit()

    return card, chat, player, game


def delete_data_test(card, chat, player, game):
    model_base.delete_record(game)
    model_base.delete_record(chat)
    model_base.delete_record(player)
    model_base.delete_record(card)
