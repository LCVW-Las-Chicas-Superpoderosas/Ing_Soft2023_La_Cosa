import unittest

from fastapi.testclient import TestClient
from game.models import Game
from main import app
from model_base import ModelBase, initialize_database
from player.models import Player
from pony.orm import db_session, commit
from tests.test_utils import create_data_test, delete_data_test


client = TestClient(app)


class TestCreateGameEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Create and initialize the database
        initialize_database()

    @classmethod
    def tearDownClass(self):
        model_base = ModelBase()
        with db_session:
            model_base.delete_record(Player.get(name='pedro'))
            model_base.delete_record(Player.get(name='pepe'))
            model_base.delete_record(Player.get(name='tomi'))
            model_base.delete_record(Player.get(name='test_player'))
            model_base.delete_record(Game.get(name='catacumbas_ok'))
    '''
    The following test cases cover possible scenarios
    for the create_game endpoint:
    - Create a game with valid data
    - Create a game with min_players > max_players
    - Create a game with min_players < 4
    - Create a game with max_players > 12
    - Create a game with a player that is already part of a game
    '''

    def test_create_game(self):
        with db_session:
            model_base = ModelBase()
            player = model_base.add_record(Player, name='test_player')
            commit()

        game_data = {
            'id_player': player.id,
            'name': 'catacumbas_ok',
            'password': '123456',
            'min_players': 4,
            'max_players': 8
        }
        response = client.post('/game', json=game_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['detail'],
            'Game catacumbas_ok created successfully.')

    def test_create_game_player_already_part_of_a_game(self):
        with db_session:
            player = Player.get(name='test_player')
        game_data = {
            'id_player': player.id,
            'name': 'catacumbas_player_already_part_of_a_game',
            'password': '123456',
            'min_players': 4,
            'max_players': 6
        }
        response = client.post('/game', json=game_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['detail'],
            'User is already part of a game.',
        )

    def test_create_game_min_players_greater_than_max_players(self):
        with db_session:
            model_base = ModelBase()
            player = model_base.add_record(Player, name='pedro')
            commit()

        game_data = {
            'id_player': player.id,
            'name': 'catacumbas_min_gt_max',
            'password': '123456',
            'min_players': 8,
            'max_players': 4
        }
        response = client.post('/game', json=game_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['detail'],
            'Incorrect range of players.' +
            ' Please check the minimum and maximum player fields.',
        )

    def test_create_game_min_players_less_than_4(self):
        with db_session:
            model_base = ModelBase()
            player = model_base.add_record(Player, name='tomi')
            commit()

        game_data = {
            'id_player': player.id,
            'name': 'catacumbas_min_gt_4',
            'password': '123456',
            'min_players': 1,
            'max_players': 12
        }
        response = client.post('/game', json=game_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['detail'],
            'Incorrect range of players.' +
            ' Please check the minimum and maximum player fields.',
        )

    def test_create_game_max_players_greater_than_12(self):
        with db_session:
            model_base = ModelBase()
            player = model_base.add_record(Player, name='pepe')
            commit()

        game_data = {
            'id_player': player.id,
            'name': 'catacumbas_max_gt_12',
            'password': '123456',
            'min_players': 4,
            'max_players': 13
        }
        response = client.post('/game', json=game_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['detail'],
            'Incorrect range of players.' +
            ' Please check the minimum and maximum player fields.',
        )


class TestGameActions(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Create and initialize the database
        initialize_database()

    def test_next_turn_ok(self):
        # Test the next_turn endpoint

        with db_session:
            card, chat, player, game = create_data_test()

            game_data = {
                'game_id': game.id,
            }

            response = client.post('/game/next_turn', json=game_data)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['detail'],
                f'Next turn for game {game.name} set successfully.')
            delete_data_test(card, chat, player, game)

    def test_next_turn_invalid_game(self):
        # Test the next_turn endpoint
        game_data = {
            'game_id': 99999,
        }
        response = client.post('/game/next_turn', json=game_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], 'Game not found.')
