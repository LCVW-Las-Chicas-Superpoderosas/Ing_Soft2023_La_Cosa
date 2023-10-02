import unittest

from fastapi.testclient import TestClient
from game.models import Game
from main import app
from model_base import ModelBase, initialize_database
from player.models import Player
from pony.orm import db_session, commit
from tests.test_utils import create_data_test, delete_data_test


client = TestClient(app)


class TestHandEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Create and initialize the database
        initialize_database()

    @classmethod
    def tearDownClass(self):
        model_base = ModelBase()
        with db_session:
            # Completar
    '''
        x
    '''

    def test_assign_cards_to_game(self):
        with db_session:
            # completar
            
    
    def test_initial_repartition_to_players(self):
        with db_session:
            # completar