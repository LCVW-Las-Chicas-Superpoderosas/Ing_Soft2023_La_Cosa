import unittest

from fastapi.testclient import TestClient
from game.models import Game
from main import app
from model_base import ModelBase, initialize_database
from player.models import Player
from pony.orm import commit, db_session
from tests.test_utils import (create_data_full_lobby,
    create_data_full_lobby_ep,
    create_data_game_not_min_players, create_data_game_not_waiting,
    create_data_incomplete_lobby, create_data_started_game,
    create_data_test, create_data_cards_given,
    create_data_cards_given2, create_data_cards_given3,
    delete_data_full_lobby)


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
            delete_data_full_lobby(card, chat, player, game)

    def test_next_turn_invalid_game(self):
        # Test the next_turn endpoint
        game_data = {
            'game_id': 99999,
        }
        response = client.post('/game/next_turn', json=game_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], 'Game not found.')


class TestStartGame(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Create and initialize the database
        initialize_database()

    def test_start_game_ok(self):
        with db_session:
            card, chat, players, game = create_data_full_lobby()

            payload = {
                'id_player': str(players[0].id)
            }
            response = client.put('/game/start', json=payload)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['detail'],
                             f'Game {game.name} started successfully.')

    def test_start_game_not_the_host(self):
        with db_session:
            card, chat, players, game = create_data_full_lobby()
            payload = {
                'id_player': str(players[3].id)
            }

            response = client.put('/game/start', json=payload)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['detail'],
                             'Only the host can start the game.')

    def test_game_is_not_startable(self):
        with db_session:
            card, chat, players, game = create_data_started_game()
            game.host = players[0].id
            payload = {
                'id_player': str(players[0].id)
            }

            response = client.put('/game/start', json=payload)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['detail'],
                             'Game cannot be started.')

    def test_player_is_not_in_game(self):
        with db_session:
            card, chat, players, game = create_data_started_game()

            payload = {
                'id_player': str(players[4].id)
            }

            response = client.put('/game/start', json=payload)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['detail'],
                             'Player is not part of a game.')


class TestJoinGame(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Create and initialize the database
        initialize_database()

    def test_join_valid_game(self):
        with db_session:
            card, chat, players, game = create_data_incomplete_lobby()

            payload = {
                'id_game': game.id,
                'id_player': players[4].id,
            }

            response = client.post('/game/join', json=payload)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['detail'],
                'Player create_data_incomplete_lobby_5 joined game ' +
                'create_data_incomplete_lobby successfully.')

    def test_join_full_game(self):
        with db_session:
            card, chat, players, game = create_data_full_lobby_ep()

            payload = {
                'id_game': game.id,
                'id_player': players[4].id,
            }

            response = client.post('/game/join', json=payload)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['detail'],
                             'Game is full.')

    def test_game_not_waiting_players(self):
        with db_session:
            card, chat, players, game = create_data_game_not_waiting()

            payload = {
                'id_game': game.id,
                'id_player': players[4].id,
            }

            response = client.post('/game/join', json=payload)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['detail'],
                             'Game is not waiting for players.')


class TestGetLobbyInfo(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Create and initialize the database
        initialize_database()

    def test_startable_lobby(self):
        with db_session:
            card, chat, players, game = create_data_full_lobby()

            headers = {
                'id-player': str(players[0].id)
            }

            response = client.get('/game/join', headers=headers)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['detail'],
                             'create_data_full_lobby lobby information.')
            self.assertEqual(response.json()['data']['is_host'], True)
            self.assertEqual(response.json()['data']['can_start'], True)

    def test_cannot_start_not_waiting(self):
        with db_session:
            card, chat, players, game = create_data_game_not_waiting()
            headers = {
                'id-player': str(players[0].id)
            }

            response = client.get('/game/join', headers=headers)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['detail'],
                             'create_data_game_not_waiting lobby information.')
            self.assertEqual(response.json()['data']['is_host'], True)
            self.assertEqual(response.json()['data']['can_start'], False)

    def test_cannot_start_full(self):
        with db_session:
            card, chat, players, game = create_data_game_not_min_players()

            headers = {
                'id-player': str(players[0].id)
            }

            response = client.get('/game/join', headers=headers)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['detail'],
                             'create_data_game_not_min_players lobby information.')
            self.assertEqual(response.json()['data']['is_host'], True)
            self.assertEqual(response.json()['data']['can_start'], False)


class TestDeleteGame(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Create and initialize the database
        initialize_database()

    def test_delete_game(self):
        with db_session:
            card, chat, players, game = create_data_full_lobby()

            data = {
                'id_game': game.id
            }

            response = client.request('DELETE', '/game/', json=data)
            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 200)

    def test_delete_game_not_valid_request(self):
        with db_session:
            card, chat, players, game = create_data_full_lobby()
            data = {
                'pepe': game.id
            }

            response = client.request('DELETE', '/game/', json=data)
            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 422)

    def test_delete_game_not_valid(self):
        with db_session:
            card, chat, players, game = create_data_full_lobby()
            data = {
                'id_game': 999
            }

            response = client.request('DELETE', '/game/', json=data)
            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 400)


class TestInitialRepartitionGame(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        initialize_database()

    def test_put_hand(self):
        with db_session:
            card, chat, players, game = create_data_cards_given()

            header = {
                'id-player': str(players[1].id)
            }

            response = client.request('PUT', '/hand/', headers=header)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['data']['picked_cards'], ['create_data_started_game_card'])
            self.assertEqual(response.json()['data']['next_card_type'], 3)

    def test_get_hand(self):
        with db_session:
            card, chat, players, game = create_data_cards_given2()

            header = {
                'id-player': str(players[0].id)
            }

            response = client.request('GET', '/hand/', headers=header)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()['data']['hand']),
                             len(['img13.png', 'img1.png', 'create_data_started_game_card', 'img12.png']))

    def test_put_and_get_game_not_started(self):
        with db_session:
            card, chat, players, game = create_data_cards_given3()

            header = {
                'id-player': str(players[1].id)
            }

            responsePut = client.request('PUT', '/hand/', headers=header)
            responseGet = client.request('GET', '/hand/', headers=header)

            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(responsePut.status_code, 400)
            self.assertEqual(responseGet.status_code, 400)


class TestListGames(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Create and initialize the database
        initialize_database()

    def test_list_valid_game(self):
        with db_session:
            # Create a joinable game
            card, chat, players, game = create_data_incomplete_lobby()

            # Make an empty GET request
            response = client.get('/game/list')
            delete_data_full_lobby(card, chat, players, game)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['detail'],
                             'Joinable games list.')
            self.assertEqual(len(response.json()['data']), 1)

    def test_list_no_game(self):
        with db_session:
            # Make an empty GET request
            response = client.get('/game/list')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['detail'],
                             'Joinable games list.')
            self.assertEqual(len(response.json()['data']), 0)

    def test_list_no_valid_games(self):
        with db_session:
            # Creates two non-joinable games
            # Case: Full game
            card, chat, players, game = create_data_full_lobby()
            # Case: Game not waiting for players
            card2, chat2, players2, game2 = create_data_game_not_waiting()

            # Make an empty GET request
            response = client.get('/game/list')
            delete_data_full_lobby(card, chat, players, game)
            delete_data_full_lobby(card2, chat2, players2, game2)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['detail'],
                             'Joinable games list.')
            self.assertEqual(len(response.json()['data']), 0)
