import json
import unittest

from card.effects_mapping import flame_torch
from card.view import router
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from mock import patch
from model_base import initialize_database, ModelBase
from player.models import Player
from pony.orm import db_session, commit
from tests.test_utils import create_data_test, delete_data_full_lobby

client = TestClient(router)

class TestPlayCard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def test_play_card_invalid_card_token(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'action': 'play_card',
                'card_token': 'test_card_fake',
                'id_player': player[0].id,
                'target_id': player[0].id
            }
            with self.assertRaises(RequestValidationError):
                with client.websocket_connect("/ws") as websocket:
                    websocket.send_text(json.dumps(payload))

            delete_data_full_lobby(card, chat, player, game)

    def test_play_card_user_not_found(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'action': 'play_card',
                'card_token': card.card_token,
                'id_player': 999,  # Use an ID that doesn't exist
                'target_id': player[0].id
            }
            with self.assertRaises(RequestValidationError):
                with client.websocket_connect("/ws") as websocket:
                    websocket.send_text(json.dumps(payload))

            delete_data_full_lobby(card, chat, player, game)

    def test_play_card_game_not_playing(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'action': 'play_card',
                'card_token': card.card_token,
                'id_player': player[0].id,
                'target_id': 999  # Use a target ID that doesn't exist
            }
            with self.assertRaises(RequestValidationError):
                with client.websocket_connect("/ws") as websocket:
                    websocket.send_text(json.dumps(payload))

            delete_data_full_lobby(card, chat, player, game)

    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: True})
    def test_play_card_with_valid_data(self, *args, **kwargs):
        with db_session:
            card, chat, player, game = create_data_test()
            game.status = 1
            commit()
            payload = {
                'action': 'play_card',
                'card_token': card.card_token,
                'id_player': player[0].id,
                'target_id': player[0].id
            }
            with client.websocket_connect("/ws") as websocket:
                websocket.send_text(json.dumps(payload))
                result = websocket.receive_text()

            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(websocket.close_code, 1000)  # WebSocket close code for clean close
        data = json.loads(result)
        self.assertEqual(data['detail'], 'Card create_data_test_card played successfully')
        self.assertEqual(data['data']['user']['id'], player[0].id)
        self.assertFalse(data['data']['the_thing_win'])
        self.assertFalse(data['data']['the_humans_win'])

    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: True})
    def test_human_win_with_valid_data(self, *args, **kwargs):
        with db_session:
            card, chat, player, game = create_data_test()
            player[0].is_alive = True
            player[1].is_alive = False
            commit()
            payload = {
                'action': 'play_card',
                'card_token': card.card_token,
                'id_player': player[0].id,
                'target_id': player[0].id
            }
            with client.websocket_connect("/ws") as websocket:
                websocket.send_text(json.dumps(payload))
                result = websocket.receive_text()

            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(websocket.close_code, 1000)  # WebSocket close code for clean close
        data = json.loads(result)
        self.assertEqual(data['detail'], 'Card create_data_test_card played successfully')
        self.assertEqual(data['data']['user']['id'], player[0].id)
        self.assertFalse(data['data']['the_thing_win'])
        self.assertTrue(data['data']['the_humans_win'])

    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: True})
    def test_thing_win_with_valid_data(self, *args, **kwargs):
        with db_session:
            card, chat, player, game = create_data_test()
            player[0].is_alive = False
            player[1].is_alive = True
            game.next_turn()
            commit()
            payload = {
                'action': 'play_card',
                'card_token': card.card_token,
                'id_player': player[1].id,
                'target_id': player[1].id
            }
            with client.websocket_connect("/ws") as websocket:
                websocket.send_text(json.dumps(payload))
                result = websocket.receive_text()

            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(websocket.close_code, 1000)  # WebSocket close code for clean close
        data = json.loads(result)
        self.assertEqual(data['detail'], 'Card create_data_test_card played successfully')
        self.assertEqual(data['data']['user']['id'], player[1].id)
        self.assertTrue(data['data']['the_thing_win'])
        self.assertFalse(data['data']['the_humans_win'])
