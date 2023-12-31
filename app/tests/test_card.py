import json
import unittest

from card.effects_mapping import flame_torch, suspicion
from card.models import Card
from card.view import router
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from mock import patch
from model_base import ModelBase, initialize_database
from player.models import Player
from pony.orm import commit, db_session
from tests.test_utils import create_data_test, delete_data_full_lobby

client = TestClient(router)


class TestPlayCard(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        initialize_database()

    @patch('card.view._validate_play', lambda *args, **kwargs: None)
    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: {'status': True, 'data': None}})
    def test_play_card_invalid_card_token(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'card_token': 'test_card_fake',
                'id_player': player[0].id,
                'target_id': player[0].id
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))
            delete_data_full_lobby(card, chat, player, game)

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

    @patch('card.view._validate_play', lambda *args, **kwargs: None)
    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: {'status': True, 'data': None}})
    def test_play_card_user_not_found(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'card_token': card.card_token,
                'id_player': 999,  # Use an ID that doesn't exist
                'target_id': player[0].id
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))
            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'User 999 not found')

    @patch('card.view._validate_play', lambda *args, **kwargs: None)
    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: {'status': True, 'data': None}})
    def test_play_card_game_not_playing(self):
        with db_session:
            card, chat, player, game = create_data_test()
            payload = {
                'card_token': card.card_token,
                'id_player': player[0].id,
                'target_id': 999  # Use a target ID that doesn't exist
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))
            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'Target user not found')

    @patch('card.view._validate_play', lambda *args, **kwargs: None)
    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: {'status': True, 'data': None}})
    def test_play_card_with_valid_data(self, *args, **kwargs):
        with db_session:
            card, chat, player, game = create_data_test()
            game.status = 1
            commit()
            payload = {
                'card_token': card.card_token,
                'id_player': player[0].id,
                'target_id': player[0].id
            }
            response = client.post('/hand/play/', data=json.dumps(payload))
            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['detail'], 'Card create_data_test_card played successfully')
        self.assertEqual(data['data']['user']['id'], player[0].id)
        self.assertFalse(data['data']['the_thing_win'])
        self.assertFalse(data['data']['the_humans_win'])

    @patch('card.view._validate_play', lambda *args, **kwargs: None)
    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: {'status': True, 'data': None}})
    def test_human_win_with_valid_data(self, *args, **kwargs):
        with db_session:
            card, chat, player, game = create_data_test()
            player[0].is_alive = True
            player[1].is_alive = False
            commit()
            payload = {
                'card_token': card.card_token,
                'id_player': player[0].id,
                'target_id': player[0].id
            }
            response = client.post('/hand/play/', data=json.dumps(payload))
            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['detail'], 'Card create_data_test_card played successfully')
        self.assertEqual(data['data']['user']['id'], player[0].id)
        self.assertFalse(data['data']['the_thing_win'])
        self.assertTrue(data['data']['the_humans_win'])

    @patch('card.view._validate_play', lambda *args, **kwargs: None)
    @patch('card.view.EFFECTS_TO_PLAYERS', {'create_data_test_card': lambda x: {'status': True, 'data': None}})
    def test_thing_win_with_valid_data(self, *args, **kwargs):
        with db_session:
            card, chat, player, game = create_data_test()
            player[0].is_alive = False
            player[1].is_alive = True
            game.next_turn()
            commit()
            payload = {
                'card_token': card.card_token,
                'id_player': player[1].id,
                'target_id': player[1].id
            }
            response = client.post('/hand/play/', data=json.dumps(payload))
            delete_data_full_lobby(card, chat, player, game)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['detail'], 'Card create_data_test_card played successfully')
        self.assertEqual(data['data']['user']['id'], player[1].id)
        self.assertTrue(data['data']['the_thing_win'])
        self.assertFalse(data['data']['the_humans_win'])


class TestCards(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        initialize_database()

    def test_flame_torch(self, *args, **kwargs):
        with db_session:
            player = ModelBase().add_record(Player, name='flame_torch_player', my_position=0)
            commit()
            result = flame_torch(player.id)
        self.assertTrue(result["status"])
        self.assertFalse(player.is_alive)

    def test_flame_torch_failed(self, *args, **kwargs):
        with db_session:
            result = flame_torch(999)

        self.assertFalse(result["status"])

    def test_suspicion(self, *args, **kwargs):
        with db_session:
            player = ModelBase().add_record(Player, name='suspicion_player', my_position=0)
            # create a Set of instances of Card
            player2 = ModelBase().add_record(Player, name='suspicion_player2', my_position=1)
            card =  ModelBase().get_first_record_by_value(Card, card_token='img22.jpg')
            player2.cards = [card]
            commit()
            result = suspicion(player2.id)
        self.assertTrue(result["status"])