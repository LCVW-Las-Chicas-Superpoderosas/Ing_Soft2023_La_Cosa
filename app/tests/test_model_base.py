import unittest

from model_base import ModelBase, initialize_database
from player.models import Player
from pony.orm import db_session


class TestModelBase(unittest.TestCase):
    initialize_database()

    def test_delete_record(self):
        # Test deleting a record
        model_base = ModelBase()  # Replace with your database URL if needed
        with db_session:
            player = model_base.add_record(Player, name='el_pepe')
            model_base.delete_record(player)
            deleted_player = model_base.get_record_by_value(Player, name='el_pepe')
            self.assertIsNone(deleted_player)

    def test_add_record(self):
        # Test adding a new record
        model_base = ModelBase()  # Replace with your database URL if needed
        with db_session:
            player = model_base.add_record(Player, name='el_pepe23')
            self.assertIsNotNone(player)
            model_base.delete_record(player)
