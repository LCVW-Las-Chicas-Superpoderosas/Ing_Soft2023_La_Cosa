from datetime import datetime

import mysql.connector
from pony.orm import Database, PrimaryKey, Required, Set, commit, select, db_session

DATABASE_URL = "localhost"
MYSQL_USER = 'root'


class ModelBase:
    def __init__(self, database_url):
        self.database_url = database_url
        # If the database does not exist, create it
        self.create_mysql_database()
        self.db = Database(   
            provider='mysql',
            host=self.database_url,
            user=MYSQL_USER,
            passwd=MYSQL_USER,
            db='ing_2023'
        )

    def initialize_database(self):
        class Card(self.db.Entity):
            id = PrimaryKey(int, auto=True)
            name = Required(str, unique=True, index=True)
            description = Required(str, unique=True, index=True)
            games = Set("Game")

        # Define entities and generate mapping for all of them
        class Game(self.db.Entity):
            id = PrimaryKey(int, auto=True)
            name = Required(str, unique=True, index=True)
            password = Required(str)
            created_at = Required(datetime, default=datetime.utcnow)
            chats = Set("Chat")
            cards = Required(Card)

        class Chat(self.db.Entity):
            id = PrimaryKey(int, auto=True)
            game = Required(Game)
            message = Required(str, unique=True, index=True)

        class Player(self.db.Entity):
            id = PrimaryKey(int, auto=True)
            name = Required(str, unique=True, index=True)
            created_at = Required(datetime, default=datetime.utcnow)

        # Generate mapping for all entities (including Player)
        self.db.generate_mapping(create_tables=True)
        self.Player = Player
        self.Card = Card
        self.Game = Game
        self.Chat = Chat

    def create_mysql_database(self):
        try:
            # Connect to MySQL server (assumes root user with no password)
            connection = mysql.connector.connect(
                host=self.database_url,
                user=MYSQL_USER,
                passwd=MYSQL_USER)

            # Create a cursor object to execute SQL commands
            cursor = connection.cursor()

            # Create the database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS ing_2023")

            # Close the cursor and the connection
            cursor.close()
            connection.close()
        except Exception as e:
            raise Exception(f"Error creating MySQL database: {e}")

    def add_record(self, entity_cls, **kwargs):
        try:
            entity = entity_cls(**kwargs)
            commit()
            return entity
        except Exception as e:
            raise Exception(f"Error adding record: {e}")

    def get_record_by_value(self, entity_cls, **kwargs):
        try:
            # Initialize the query with the entity class
            query = select(c for c in entity_cls)

            # Add conditions based on the key-value pairs in kwargs
            for key, value in kwargs.items():
                query = query.filter(lambda c: getattr(c, key) == value)

            # Retrieve the first matching record or None
            record = query.first()
            return record

        except Exception as e:
            print(f"Error retrieving record: {e}")
            return None

    def update_record(self, record):
        try:
            commit()
        except Exception as e:
            raise Exception(f"Error updating record: {e}")

    def delete_record(self, record):
        try:
            record.delete()
            commit()
        except Exception as e:
            raise Exception(f"Error deleting record: {e}")


if __name__ == "__main__":
    model_base = ModelBase(DATABASE_URL)
    model_base.initialize_database()

    # Example of usage:

    # Create a new player
    with db_session:
        model_base.add_record(model_base.Player, id=32, name="aaa", created_at=datetime.utcnow())

        # Read a player by ID
        user = model_base.get_record_by_value(model_base.Player, name="aaa", id=32)
        if user:
            print(user.name, user.created_at)
        else:
            print("User not found")
        if user:
            # Modify a player
            user.name = "new_username"
            model_base.update_record(user)

        if user:
            # Delete a player
            model_base.delete_record(user)
