import unittest
from fastapi.testclient import TestClient
from main import app
from model_base import initialize_database


class TestCreateGameEndpoint(unittest.TestCase):
    initialize_database()
    client = TestClient(app)

    """
    The following test cases cover possible scenarios for the create_game endpoint:
    - Create a game with valid data
    - Create a game with min_players > max_players
    - Create a game with min_players < 4
    - Create a game with max_players > 12
    - Create a game with a player that is already part of a game

    """

    def test_create_game(self):
        game_data = {
            'id_player': 1,
            'name': 'catacumbas_ok',
            'password': '123456',
            'min_players': 4,
            'max_players': 8,
        }
        response = self.client.post('/game', json=game_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()['detail'], 'Game catacumbas_ok created successfully.'
        )
        self.assertTrue(isinstance(response.json()['data']['game_id'], int))
        self.assertTrue(response.json()['data']['game_id'] > 0)

    def test_create_game_min_players_greater_than_max_players(self):
        game_data = {
            'id_player': 2,
            'name': 'catacumbas_min_gt_max',
            'password': '123456',
            'min_players': 8,
            'max_players': 4,
        }
        response = self.client.post('/game', json=game_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['detail'],
            'Incorrect range of players. Please check the minimum and maximum player fields.',
        )

    def test_create_game_min_players_less_than_4(self):
        game_data = {
            'id_player': 3,
            'name': 'catacumbas_min_gt_4',
            'password': '123456',
            'min_players': 1,
            'max_players': 12,
        }
        response = self.client.post('/game', json=game_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['detail'],
            'Incorrect range of players. Please check the minimum and maximum player fields.',
        )

    def test_create_game_max_players_greater_than_12(self):
        game_data = {
            'id_player': 4,
            'name': 'catacumbas_max_gt_12',
            'password': '123456',
            'min_players': 4,
            'max_players': 13,
        }
        response = self.client.post('/game', json=game_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['detail'],
            'Incorrect range of players. Please check the minimum and maximum player fields.',
        )

    def test_create_game_player_already_part_of_a_game(self):
        game_data = {
            'id_player': 1,
            'name': 'catacumbas_player_already_part_of_a_game',
            'password': '123456',
            'min_players': 4,
            'max_players': 6,
        }
        response = self.client.post('/game', json=game_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['detail'],
            'User is already part of a game.',
        )
