from pony.orm import Database, commit, select, db_session

DATABASE_URL = "localhost"
MYSQL_USER = 'root'

Models = Database(
    provider='mysql',
    host=DATABASE_URL,
    user=MYSQL_USER,
    passwd=MYSQL_USER,
    db='ing_2023'
)


class ModelBase:
    def __init__(self):
        self.database_url = DATABASE_URL

    def get_all_entry_of_entity(self, entity_cls):
        entries = select(c for c in entity_cls)[:]  # Use the select query to get all entities
        return [card.to_dict() for card in entries]

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


def initialize_database():
    # Generate mapping for all entities (including Player)
    try:
        Models.generate_mapping(create_tables=True)
    except Exception as e:
        print(f"Error: {e}")
