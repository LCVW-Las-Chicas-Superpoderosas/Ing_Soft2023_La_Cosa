from create_mysql_db import create_database
from fastapi.testclient import TestClient
from main import app
from model_base import initialize_database
from pony.orm import db_session, commit
from player.models import Player
import unittest
import os
from tests.test_utils import create_data_player_retrieve_defense_cards_test

CLIENT = TestClient(app)


class TestRegisterEndpoint(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create and initialize the database
        create_database(os.environ['DATABASE_NAME_LC'])
        initialize_database()

    def setUp(self):
        self.request_body = {'name': 'test_player_1'}

    def test_register_player(self):
        # Define a test request body

        # Send a POST request to the /register endpoint
        response = CLIENT.post('/register', json=self.request_body)

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check the response content
        data = response.json()
        self.assertIn('status_code', data)
        self.assertIn('detail', data)
        self.assertIn('data', data)

        # Optionally, you can perform additional
        # assertions on the response data
        self.assertEqual(data['status_code'], 200)
        self.assertEqual(data['detail'],
            f"User {self.request_body['name']} registered successfully")

    def tearDown(self):
        # Clean up the database by deleting the test user
        with db_session:
            # Assuming you have a method to find and delete a user by name
            user = Player.get(name=self.request_body['name'])
            if user:
                user.delete()
                commit()

    def test_register_player_error(self):
        # Define a test request body

        # Send a POST request to the /register endpoint
        response = CLIENT.post('/register', json=self.request_body)

        # Send a POST request to the /register endpoint
        response = CLIENT.post('/register', json=self.request_body)

        # Check the response status code
        self.assertEqual(response.status_code, 500)

        # Check the response content
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('IntegrityError', data['detail'])


class TestFunPlayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_database(os.environ['DATABASE_NAME_LC'])
        initialize_database()

    def test_retrieve_defense_card_functions(self):
        with db_session:
            player1, player2 = create_data_player_retrieve_defense_cards_test()

            # player 1 with all cards

            tienelanzallamasdef = player1.check_defense_of_card_attack_in_hand(24)

            tieneaquiestoybien = player1.check_defense_of_card_attack_in_hand(54)

            cartasdedefensaattack = player1.return_defense_cards_of_attack(24)

            tieneaterrador = player1.check_defense_of_exchange_in_hand()

            cartasdeexchange = player1.return_defense_cards_of_exchange()

            # player 2 with no cards

            tienelanzallamasdef2 = player2.check_defense_of_card_attack_in_hand(24)

            tieneaquiestoybien2 = player2.check_defense_of_card_attack_in_hand(54)

            cartasdedefensaattack2 = player2.return_defense_cards_of_attack(24)

            tieneaterrador2 = player2.check_defense_of_exchange_in_hand()

            cartasdeexchange2 = player2.return_defense_cards_of_exchange()

            # assert player 1

            self.assertEqual(tienelanzallamasdef, True)
            self.assertEqual(tieneaquiestoybien, True)
            self.assertEqual(tieneaterrador, True)
            self.assertEqual(len(cartasdedefensaattack), len([{'card_tokens': 'img81.jpg'}]))
            self.assertEqual(len(cartasdeexchange), len([{'card_tokens': 'img69.jpg'},
                                                 {'card_tokens': 'img79.jpg'}, {'card_tokens': 'img74.jpg'}]))

            # assert player 2

            self.assertEqual(tienelanzallamasdef2, False)
            self.assertEqual(tieneaquiestoybien2, False)
            self.assertEqual(tieneaterrador2, False)
            self.assertEqual(cartasdedefensaattack2, [])
            self.assertEqual(cartasdeexchange2, [])
