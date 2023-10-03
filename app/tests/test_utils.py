import json

from card.models import Card, CardType
from chat.models import Chat
from game.models import Game
from model_base import ModelBase
from player.models import Player
from pony.orm import commit

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


def create_data_full_lobby():
    for i in range(16):
        model_base.add_record(Card, name='test_card',
            card_token='test_card' + str(i),
            number=0,
            type=CardType.PANIC.value)

    chat = model_base.add_record(Chat)
    player1 = model_base.add_record(Player, name='player1',
        id=1000)
    player2 = model_base.add_record(Player, name='player2')
    player3 = model_base.add_record(Player, name='player3')
    player4 = model_base.add_record(Player, name='player4')

    game = model_base.add_record(Game, name='test', password='', chats=chat,
        cards=model_base.get_records_by_value(Card, name='test_card'),
        players=[player1, player2, player3, player4],
        host=1000, min_players=4, max_players=4)

    commit()
    return game.cards, chat, [player1, player2, player3, player4], game


def create_data_started_game():
    card = model_base.add_record(Card, name='test_card',
        card_token='test_card', type=CardType.PANIC.value)
    chat = model_base.add_record(Chat)
    player1 = model_base.add_record(Player, name='player1', cards=card,
        id=1000)
    player2 = model_base.add_record(Player, name='player2', cards=card)
    player3 = model_base.add_record(Player, name='player3', cards=card)
    player4 = model_base.add_record(Player, name='player4', cards=card)
    player5 = model_base.add_record(Player, name='player5', cards=card)

    game = model_base.add_record(Game, name='test', password='', chats=chat,
        cards=card, players=[player1, player2, player3, player4], host=1000,
        min_players=4, max_players=4, status=1)

    commit()

    return card, chat, [player1, player2, player3, player4, player5], game


def delete_data_full_lobby(cards, chat, players, game):
    for player in players:
        model_base.delete_record(player)
    try:
        for card in cards:
            model_base.delete_record(card)
    except Exception:
        model_base.delete_record(cards)
    model_base.delete_record(game)
    model_base.delete_record(chat)

def delete_data_test(card, chat, player, game):
    model_base.delete_record(game)
    model_base.delete_record(chat)
    model_base.delete_record(player)
    model_base.delete_record(card)


def create_data_incomplete_lobby():
    card = model_base.add_record(Card, name='test_card',
        card_token='test_card', type=CardType.PANIC.value)
    chat = model_base.add_record(Chat)
    player1 = model_base.add_record(Player, name='player1', cards=card,
        id=1000)
    player2 = model_base.add_record(Player, name='player2', cards=card)
    player3 = model_base.add_record(Player, name='player3', cards=card)
    player4 = model_base.add_record(Player, name='player4', cards=card)
    player5 = model_base.add_record(Player, name='player5', cards=card)

    game = model_base.add_record(Game, name='test', password='', chats=chat,
        cards=card, players=[player1, player2, player3, player4], host=1000,
        min_players=4, max_players=5)

    commit()

    return card, chat, [player1, player2, player3, player4, player5], game


def create_data_full_lobby_ep():
    card = model_base.add_record(Card, name='test_card',
        card_token='test_card', type=CardType.PANIC.value)
    chat = model_base.add_record(Chat)
    player1 = model_base.add_record(Player, name='player1', cards=card,
        id=1000)
    player2 = model_base.add_record(Player, name='player2', cards=card)
    player3 = model_base.add_record(Player, name='player3', cards=card)
    player4 = model_base.add_record(Player, name='player4', cards=card)
    player5 = model_base.add_record(Player, name='player5', cards=card)

    game = model_base.add_record(Game, name='test', password='', chats=chat,
        cards=card, players=[player1, player2, player3, player4], host=1000,
        min_players=4, max_players=4)

    commit()

    return card, chat, [player1, player2, player3, player4, player5], game


def create_data_game_not_waiting():
    card = model_base.add_record(Card, name='test_card',
        card_token='test_card', type=CardType.PANIC.value)
    chat = model_base.add_record(Chat)
    player1 = model_base.add_record(Player, name='player1', cards=card,
        id=1000)
    player2 = model_base.add_record(Player, name='player2', cards=card)
    player3 = model_base.add_record(Player, name='player3', cards=card)
    player4 = model_base.add_record(Player, name='player4', cards=card)
    player5 = model_base.add_record(Player, name='player5', cards=card)

    game = model_base.add_record(Game, name='test', password='', chats=chat,
        cards=card, players=[player1, player2, player3, player4], host=1000,
        min_players=4, max_players=5, status=1)

    commit()

    return card, chat, [player1, player2, player3, player4, player5], game


def create_data_game_not_min_players():
    card = model_base.add_record(Card, name='test_card',
        card_token='test_card', type=CardType.PANIC.value)
    chat = model_base.add_record(Chat)
    player1 = model_base.add_record(Player, name='player1', cards=card,
        id=1000)
    player2 = model_base.add_record(Player, name='player2', cards=card)
    player3 = model_base.add_record(Player, name='player3', cards=card)

    game = model_base.add_record(Game, name='test', password='', chats=chat,
        cards=card, players=[player1, player2, player3], host=1000,
        min_players=4, max_players=5)

    commit()

    return card, chat, [player1, player2, player3], game