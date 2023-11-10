import json
import unittest

from card.view import router
from fastapi.testclient import TestClient
from mock import patch
from model_base import initialize_database
from pony.orm import db_session, commit
from tests.test_utils import (create_data_test,
    delete_data_full_lobby, create_data_started_game_set_positions)


client = TestClient(router)


class TestWs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def test_play_card_invalid_card_token(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'content': {
                    'card_token': 'test_card_fake',
                    'id_player': player[0].id,
                    'target_id': player[0].id
                }
            }
            with client.websocket_connect('/ws/hand_play') as websocket:
                websocket.send_text(json.dumps(payload))
                data = json.loads(websocket.receive_text())
            delete_data_full_lobby(card, chat, player, game)
        self.assertEqual(data['status_code'], 400)

    def test_play_card_user_not_found(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'content': {
                    'card_token': card.card_token,
                    'id_player': 999,  # Use an ID that doesn't exist
                    'target_id': player[0].id
                }
            }
            with client.websocket_connect('/ws/hand_play') as websocket:
                websocket.send_text(json.dumps(payload))
                data = json.loads(websocket.receive_text())
            delete_data_full_lobby(card, chat, player, game)
        self.assertEqual(data['detail'], f'User {999} not found')

    def test_play_card_game_not_playing(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'content': {
                    'card_token': card.card_token,
                    'id_player': player[0].id,
                    'target_id': 999  # Use a target ID that doesn't exist
                }
            }
            with client.websocket_connect('/ws/hand_play') as websocket:
                websocket.send_text(json.dumps(payload))
                data = json.loads(websocket.receive_text())
            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(data['status_code'], 400)

    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: True})
    def test_play_card_with_valid_data(self, *args, **kwargs):
        with db_session:
            card, chat, player, game = create_data_test()
            game.status = 1
            commit()
            payload = {
                'content': {'card_token': card.card_token,
                'id_player': player[0].id,
                'target_id': player[0].id}
            }
            with client.websocket_connect('/ws/hand_play') as websocket:
                websocket.send_text(json.dumps(payload))
                data = json.loads(websocket.receive_text())
            delete_data_full_lobby(card, chat, player, game)

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
                'content': {'card_token': card.card_token,
                'id_player': player[0].id,
                'target_id': player[0].id}
            }
            with client.websocket_connect('/ws/hand_play') as websocket:
                websocket.send_text(json.dumps(payload))
                data = json.loads(websocket.receive_text())
            delete_data_full_lobby(card, chat, player, game)

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
                'content': {'card_token': card.card_token,
                'id_player': player[1].id,
                'target_id': player[1].id}
            }
            with client.websocket_connect('/ws/hand_play') as websocket:
                websocket.send_text(json.dumps(payload))
                data = json.loads(websocket.receive_text())

            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(data['detail'], 'Card create_data_test_card played successfully')
        self.assertEqual(data['data']['user']['id'], player[1].id)
        self.assertTrue(data['data']['the_thing_win'])
        self.assertFalse(data['data']['the_humans_win'])

    def test_get_valid_game_info(self):
        with db_session:
            # Create started game with positions set
            card, chat, players, game = create_data_started_game_set_positions()

            payload = {
                'id_player': str(players[0].id)
            }

            with client.websocket_connect('/ws/game_status') as websocket:
                websocket.send_text(json.dumps({'content': payload}))
                data = json.loads(websocket.receive_text())
            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(data['status_code'], 200)
            self.assertEqual(data['detail'],
                             'create_data_started_game_set_positions information.')
            # get the players and sort them by id
            players = data['data']['players']
            players.sort(key=lambda x: x['id'])
            self.assertEqual(players[0]['position'], 0)
            self.assertEqual(players[1]['position'], 1)
            self.assertEqual(players[2]['position'], 2)
            self.assertEqual(players[3]['position'], 3)
            self.assertEqual(data['data']['current_player'], players[0]['id'])
