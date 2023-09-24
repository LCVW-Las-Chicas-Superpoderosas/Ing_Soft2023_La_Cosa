import json
import unittest

from card.models import Card, CardType
from card.view import router
from chat.models import Chat
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from game.models import Game
from mock import patch
from model_base import ModelBase
from player.models import Player
from pony.orm import db_session

client = TestClient(router)


class TestPlayCard(unittest.TestCase):
    def setUp(self):
        with db_session:
            model_base = ModelBase()
            self.card = model_base.add_record(Card, name='test_card',
                card_token='test_card', type=CardType.PANIC.value)
            self.chat = model_base.add_record(Chat)
            self.player = model_base.add_record(Player, name='test', cards=self.card)
            self.game = model_base.add_record(Game, name='test', password='', chats=self.chat,
                cards=self.card, players=self.player)

    def tearDown(self):
        with db_session:
            model_base = ModelBase()
            model_base.delete_record(model_base.get_record_by_value(Game, name='test'))
            model_base.delete_record(model_base.get_record_by_value(Card, name='test_card'))
            model_base.delete_record(model_base.get_record_by_value(Player, name='test'))

    def test_play_card_invalid_card_token(self):
        payload = {
            'card_token': 'test_card_fake',
            'id_usuario': self.player.id,
            'target_id': self.player.id
        }
        with self.assertRaises(HTTPException) as context:
            client.post('/hand/play/', data=json.dumps(payload))

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
        payload = {
            'card_token': 'test_card',
            'id_usuario': 999,  # Use an ID that doesn't exist
            'target_id': self.player.id
        }
        with self.assertRaises(HTTPException) as context:
            client.post('/hand/play/', data=json.dumps(payload))

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'User 999 not found')

    def test_play_card_target_not_found(self):
        payload = {
            'card_token': 'test_card',
            'id_usuario': self.player.id,
            'target_id': 999  # Use a target ID that doesn't exist
        }
        with self.assertRaises(HTTPException) as context:
            client.post('/hand/play/', data=json.dumps(payload))

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'Target user not found')

    @patch('card.view.EFFECTS_TO_PLAYERS', {'test_card': lambda x: True})
    def test_play_card_with_valid_data(self, *args, **kwargs):
        payload = {
            'card_token': 'test_card',
            'id_usuario': self.player.id,
            'target_id': self.player.id
        }
        response = client.post('/hand/play/', data=json.dumps(payload))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['detail'], 'Card test_card played successfully')
