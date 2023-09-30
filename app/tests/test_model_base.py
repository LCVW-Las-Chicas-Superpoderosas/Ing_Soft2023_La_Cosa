import unittest

from model_base import ModelBase, initialize_database
from create_mysql_db import create_database
from player.models import Player
from pony.orm import db_session


class TestModelBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create and initialize the database
        create_database('ing_2023')
        initialize_database()

    def setUp(self):
        # Create a new instance of ModelBase for each test case
        self.model_base = ModelBase()

    def test_delete_record(self):
        # Test deleting a record
        with db_session:
            player = self.model_base.add_record(Player, name='el_pepe')
            self.model_base.delete_record(player)
            deleted_player = self.model_base.get_first_record_by_value(Player, name='el_pepe')
            self.assertIsNone(deleted_player)

    def test_add_record(self):
        # Test adding a new record
        with db_session:
            player = self.model_base.add_record(Player, name='el_pepe23')
            self.assertIsNotNone(player)
            self.model_base.delete_record(player)
