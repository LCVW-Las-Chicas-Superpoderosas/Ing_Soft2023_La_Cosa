from fastapi.testclient import TestClient
from main import app  # Replace 'main' with the name of your FastAPI app file
from pony.orm import db_session, commit
from player.models import Player
import unittest
from model_base import initialize_database
from create_mysql_db import create_database

CLIENT = TestClient(app)


class TestRegisterEndpoint(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create and initialize the database
        create_database('ing_2023')
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
