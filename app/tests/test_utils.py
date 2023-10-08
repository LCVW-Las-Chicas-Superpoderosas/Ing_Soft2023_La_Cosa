import json

from card.models import Card, CardType
from chat.models import Chat
from game.models import Game
from model_base import ModelBase
from player.models import Player
from pony.orm import commit

model_base = ModelBase()


def create_data_test():
    try:
        card = model_base.add_record(Card, name='create_data_test_card',
            card_token='create_data_test_card', type=CardType.PANIC.value)
        chat = model_base.add_record(Chat)
        player = model_base.add_record(Player, name='create_data_test', cards=card)
        commit()

        game = model_base.add_record(Game, name='create_data_test', password='', chats=chat,
            cards=card, players=player, host=player.id, min_players=4, max_players=8,
            turns=json.dumps([player.id]))
        commit()
    except Exception:
        card = model_base.get_first_record_by_value(Card, card_token='create_data_test_card')
        chat = model_base.get_first_record_by_value(Chat)
        player = model_base.get_first_record_by_value(Player, name='create_data_test')
        game = model_base.get_first_record_by_value(Game, name='create_data_test')
    return card, chat, player, game


def create_data_full_lobby():
    try:
        for i in range(16):
            model_base.add_record(Card, name='create_data_full_lobby_card',
                card_token='create_data_full_lobby_card' + str(i),
                number=0,
                type=CardType.PANIC.value)

        chat = model_base.add_record(Chat)
        player1 = model_base.add_record(Player, name='create_data_full_lobby_1')
        player2 = model_base.add_record(Player, name='create_data_full_lobby_2')
        player3 = model_base.add_record(Player, name='create_data_full_lobby_3')
        player4 = model_base.add_record(Player, name='create_data_full_lobby_4')
        commit()

        game = model_base.add_record(Game, name='create_data_full_lobby', password='', chats=chat,
            cards=model_base.get_records_by_value(Card, name='create_data_full_lobby_card'),
            players=[player1, player2, player3, player4],
            host=player1.id, min_players=4, max_players=4)
        commit()
    except Exception:
        game = model_base.get_first_record_by_value(Game, name='create_data_full_lobby')
        chat = model_base.get_first_record_by_value(Chat)
        player1 = model_base.get_first_record_by_value(Player, name='create_data_full_lobby_1')
        player2 = model_base.get_first_record_by_value(Player, name='create_data_full_lobby_2')
        player3 = model_base.get_first_record_by_value(Player, name='create_data_full_lobby_3')
        player4 = model_base.get_first_record_by_value(Player, name='create_data_full_lobby_4')
    return game.cards, chat, [player1, player2, player3, player4], game


def create_data_started_game():
    try:
        card = model_base.add_record(Card, name='create_data_started_game_card',
            card_token='create_data_started_game_card', type=CardType.PANIC.value)
        chat = model_base.add_record(Chat)
        player1 = model_base.add_record(Player, name='create_data_started_game_1', cards=card)
        player2 = model_base.add_record(Player, name='create_data_started_game_2', cards=card)
        player3 = model_base.add_record(Player, name='create_data_started_game_3', cards=card)
        player4 = model_base.add_record(Player, name='create_data_started_game_4', cards=card)
        player5 = model_base.add_record(Player, name='create_data_started_game_5', cards=card)
        commit()

        game = model_base.add_record(Game, name='create_data_started_game', password='', chats=chat,
            cards=card, players=[player1, player2, player3, player4], host=player1.id,
            min_players=4, max_players=4, status=1)

        commit()
    except Exception:
        game = model_base.get_first_record_by_value(Game, name='create_data_started_game')
        chat = model_base.get_first_record_by_value(Chat)
        player1 = model_base.get_first_record_by_value(Player, name='create_data_started_game_1')
        player2 = model_base.get_first_record_by_value(Player, name='create_data_started_game_2')
        player3 = model_base.get_first_record_by_value(Player, name='create_data_started_game_3')
        player4 = model_base.get_first_record_by_value(Player, name='create_data_started_game_4')
        player5 = model_base.get_first_record_by_value(Player, name='create_data_started_game_5')
        card = model_base.get_first_record_by_value(Card, card_token='create_data_started_game_card')

    return card, chat, [player1, player2, player3, player4, player5], game


def create_data_incomplete_lobby():
    try:
        card = model_base.add_record(Card, name='create_data_incomplete_lobby_card',
            card_token='create_data_incomplete_lobby_card', type=CardType.PANIC.value)
        chat = model_base.add_record(Chat)
        player1 = model_base.add_record(Player, name='create_data_incomplete_lobby_1', cards=card)
        player2 = model_base.add_record(Player, name='create_data_incomplete_lobby_2', cards=card)
        player3 = model_base.add_record(Player, name='create_data_incomplete_lobby_3', cards=card)
        player4 = model_base.add_record(Player, name='create_data_incomplete_lobby_4', cards=card)
        player5 = model_base.add_record(Player, name='create_data_incomplete_lobby_5', cards=card)
        commit()

        game = model_base.add_record(Game, name='create_data_incomplete_lobby', password='', chats=chat,
            cards=card, players=[player1, player2, player3, player4], host=player1.id,
            min_players=4, max_players=5)

        commit()

    except Exception:
        game = model_base.get_first_record_by_value(Game, name='create_data_incomplete_lobby')
        chat = model_base.get_first_record_by_value(Chat)
        player1 = model_base.get_first_record_by_value(Player, name='create_data_incomplete_lobby_1')
        player2 = model_base.get_first_record_by_value(Player, name='create_data_incomplete_lobby_2')
        player3 = model_base.get_first_record_by_value(Player, name='create_data_incomplete_lobby_3')
        player4 = model_base.get_first_record_by_value(Player, name='create_data_incomplete_lobby_4')
        player5 = model_base.get_first_record_by_value(Player, name='create_data_incomplete_lobby_5')
        card = model_base.get_first_record_by_value(Card, card_token='create_data_incomplete_lobby_card')

    return card, chat, [player1, player2, player3, player4, player5], game


def create_data_full_lobby_ep():
    try:
        card = model_base.add_record(Card, name='create_data_full_lobby_ep_card',
            card_token='create_data_full_lobby_ep_card', type=CardType.PANIC.value)
        chat = model_base.add_record(Chat)
        player1 = model_base.add_record(Player, name='create_data_full_lobby_ep_1', cards=card)
        player2 = model_base.add_record(Player, name='create_data_full_lobby_ep_2', cards=card)
        player3 = model_base.add_record(Player, name='create_data_full_lobby_ep_3', cards=card)
        player4 = model_base.add_record(Player, name='create_data_full_lobby_ep_4', cards=card)
        player5 = model_base.add_record(Player, name='create_data_full_lobby_ep_5', cards=card)
        commit()

        game = model_base.add_record(Game, name='create_data_full_lobby_ep', password='', chats=chat,
            cards=card, players=[player1, player2, player3, player4], host=player1.id,
            min_players=4, max_players=4)
        commit()
    except Exception:
        game = model_base.get_first_record_by_value(Game, name='create_data_full_lobby_ep')
        chat = model_base.get_first_record_by_value(Chat)
        player1 = model_base.get_first_record_by_value(Player, name='create_data_full_lobby_ep_1')
        player2 = model_base.get_first_record_by_value(Player, name='create_data_full_lobby_ep_2')
        player3 = model_base.get_first_record_by_value(Player, name='create_data_full_lobby_ep_3')
        player4 = model_base.get_first_record_by_value(Player, name='create_data_full_lobby_ep_4')
        player5 = model_base.get_first_record_by_value(Player, name='create_data_full_lobby_ep_5')
        card = model_base.get_first_record_by_value(Card, card_token='create_data_full_lobby_ep_card')

    return card, chat, [player1, player2, player3, player4, player5], game


def create_data_game_not_waiting():
    try:
        card = model_base.add_record(Card, name='create_data_game_not_waiting_card',
            card_token='create_data_game_not_waiting_card', type=CardType.PANIC.value)
        chat = model_base.add_record(Chat)
        player1 = model_base.add_record(Player, name='create_data_game_not_waiting_1', cards=card)
        player2 = model_base.add_record(Player, name='create_data_game_not_waiting_2', cards=card)
        player3 = model_base.add_record(Player, name='create_data_game_not_waiting_3', cards=card)
        player4 = model_base.add_record(Player, name='create_data_game_not_waiting_4', cards=card)
        player5 = model_base.add_record(Player, name='create_data_game_not_waiting_5', cards=card)
        commit()

        game = model_base.add_record(Game, name='create_data_game_not_waiting', password='', chats=chat,
            cards=card, players=[player1, player2, player3, player4], host=player1.id,
            min_players=4, max_players=5, status=1)

        commit()

    except Exception:
        game = model_base.get_first_record_by_value(Game, name='create_data_game_not_waiting')
        chat = model_base.get_first_record_by_value(Chat)
        player1 = model_base.get_first_record_by_value(Player, name='create_data_game_not_waiting_1')
        player2 = model_base.get_first_record_by_value(Player, name='create_data_game_not_waiting_2')
        player3 = model_base.get_first_record_by_value(Player, name='create_data_game_not_waiting_3')
        player4 = model_base.get_first_record_by_value(Player, name='create_data_game_not_waiting_4')
        player5 = model_base.get_first_record_by_value(Player, name='create_data_game_not_waiting_5')
        card = model_base.get_first_record_by_value(Card, card_token='create_data_game_not_waiting_card')

    return card, chat, [player1, player2, player3, player4, player5], game


def create_data_game_not_min_players():
    try:
        card = model_base.add_record(Card, name='create_data_game_not_min_players_card',
            card_token='create_data_game_not_min_players_card', type=CardType.PANIC.value)
        chat = model_base.add_record(Chat)
        player1 = model_base.add_record(Player, name='create_data_game_not_min_players_1', cards=card)
        player2 = model_base.add_record(Player, name='create_data_game_not_min_players_2', cards=card)
        player3 = model_base.add_record(Player, name='create_data_game_not_min_players_3', cards=card)
        commit()

        game = model_base.add_record(Game, name='create_data_game_not_min_players', password='', chats=chat,
            cards=card, players=[player1, player2, player3], host=player1.id,
            min_players=4, max_players=5)

        commit()

    except Exception:
        game = model_base.get_first_record_by_value(Game, name='create_data_game_not_min_players')
        chat = model_base.get_first_record_by_value(Chat)
        player1 = model_base.get_first_record_by_value(Player, name='create_data_game_not_min_players_1')
        player2 = model_base.get_first_record_by_value(Player, name='create_data_game_not_min_players_2')
        player3 = model_base.get_first_record_by_value(Player, name='create_data_game_not_min_players_3')
        card = model_base.get_first_record_by_value(Card, card_token='create_data_game_not_min_players_card')

    return card, chat, [player1, player2, player3], game


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
