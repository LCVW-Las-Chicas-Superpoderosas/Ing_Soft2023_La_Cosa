import json
import unittest

from card.view import router
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from mock import patch
from model_base import initialize_database
from pony.orm import db_session, commit
from tests.test_utils import create_data_test, delete_data_test


client = TestClient(router)


class TestPlayCard(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        initialize_database()

    def test_play_card_invalid_card_token(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'card_token': 'test_card_fake',
                'id_player': player.id,
                'target_id': player.id
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))
            delete_data_test(card, chat, player, game)

        # Check that the raised exception has a status code of 400
        self.assertEqual(context.exception.status_code, 400)
        # You can also check the exception detail message if needed
        self.assertEqual(context.exception.detail, 'Card token: test_card_fake not found')

    def test_play_card_invalid_request(self):
        payload = {
            'bad': -1,
            'request': ''
        }
        with self.assertRaises(RequestValidationError):
            client.post('/hand/play/', data=json.dumps(payload))

    def test_play_card_user_not_found(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'card_token': card.card_token,
                'id_player': 999,  # Use an ID that doesn't exist
                'target_id': player.id
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))
            delete_data_test(card, chat, player, game)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'User 999 not found')

    def test_play_card_game_not_playing(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'card_token': card.card_token,
                'id_player': player.id,
                'target_id': 999  # Use a target ID that doesn't exist
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))
            delete_data_test(card, chat, player, game)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'Game create_data_test is not in progress')

    def test_play_card_target_not_found(self):
        with db_session:
            card, chat, player, game = create_data_test()
            game.status = 1
            commit()
            payload = {
                'card_token': card.card_token,
                'id_player': player.id,
                'target_id': 999  # Use a target ID that doesn't exist
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))
            delete_data_test(card, chat, player, game)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'Target user not found')

    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: True})
    def test_play_card_with_valid_data(self, *args, **kwargs):
        with db_session:
            card, chat, player, game = create_data_test()
            game.status = 1
            commit()
            payload = {
                'card_token': card.card_token,
                'id_player': player.id,
                'target_id': player.id
            }
            response = client.post('/hand/play/', data=json.dumps(payload))
            delete_data_test(card, chat, player, game)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['detail'], 'Card create_data_test_card played successfully')
        self.assertEqual(data['data']['user']['id'], player.id)
        self.assertTrue(data['data']['game_over'])
