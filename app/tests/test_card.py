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
from model_base import ModelBase, initialize_database
from player.models import Player
from pony.orm import db_session, commit
from pony.orm.core import TransactionIntegrityError


client = TestClient(router)


class TestPlayCard(unittest.TestCase):

    def _create_data_test(self):
        model_base = ModelBase()
        card = model_base.add_record(Card, name='test_card',
            card_token='test_card', type=CardType.PANIC.value)
        player = model_base.add_record(Player, name='test', cards=card)
        chat= model_base.add_record(Chat)
        game = model_base.add_record(Game, name='test',
            password='', chats=chat, cards=card, players=player)

        commit()
        return card, player, chat, game

    def _remove_test_data(self, card, player, chat, game):
        model_base = ModelBase()
        model_base.delete_record(game)
        model_base.delete_record(chat)
        model_base.delete_record(player)
        model_base.delete_record(card)
        commit()

    @classmethod
    def setUpClass(self):
        # Create and initialize the database
        initialize_database()

    def test_play_card_invalid_card_token(self):
        with db_session:
            card, player, chat, game = self._create_data_test()
            payload = {
                'card_token': 'test_card_fake',
                'id_usuario': player.id,
                'target_id': player.id
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))

            # Check that the raised exception has a status code of 400
            self.assertEqual(context.exception.status_code, 400)
            # You can also check the exception detail message if needed
            self.assertEqual(context.exception.detail, 'Card token: test_card_fake not found')
            self._remove_test_data(card, player, chat, game)

    def test_play_card_invalid_request(self):
        payload = {
            'bad': -1,
            'request': ''
        }
        with self.assertRaises(RequestValidationError):
            client.post('/hand/play/', data=json.dumps(payload))

    def test_play_card_user_not_found(self):
        with db_session:
            card, player, chat, game = self._create_data_test()

            payload = {
                'card_token': 'test_card',
                'id_usuario': 999,  # Use an ID that doesn't exist
                'target_id': player.id
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))
            self.assertEqual(context.exception.status_code, 400)
            self.assertEqual(context.exception.detail, 'User 999 not found')
            self._remove_test_data(card, player, chat, game)

    def test_play_card_target_not_found(self):
        with db_session:
            card, player, chat, game = self._create_data_test()
            
            payload = {
                'card_token': 'test_card',
                'id_usuario': player.id,
                'target_id': -1 # Use a target ID that doesn't exist
            }
            with self.assertRaises(HTTPException) as context:
                client.post('/hand/play/', data=json.dumps(payload))

            self.assertEqual(context.exception.status_code, 400)
            self.assertEqual(context.exception.detail, 'Target user not found')

            self._remove_test_data(card, player, chat, game)

    @patch('card.view.EFFECTS_TO_PLAYERS', {'test_card': lambda x: True})
    def test_play_card_with_valid_data(self, *args, **kwargs):
        with db_session:
            card, player, chat, game = self._create_data_test()

            payload = {
                'card_token': 'test_card',
                'id_usuario': player.id,
                'target_id': player.id
            }
            response = client.post('/hand/play/', data=json.dumps(payload))

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['detail'], 'Card test_card played successfully')
            self._remove_test_data(card, player, chat, game)