from pony.orm import Database, select, db_session
from constants import DATABASE_URL, MYSQL_USER, MYSQL_PASS


Models = Database(
    provider='mysql',
    host=DATABASE_URL,
    user=MYSQL_USER,
    passwd=MYSQL_PASS,
    db='ing_2023'
)


class ModelBase:
    def get_all_entry_of_entity(self, entity_cls):
        entries = select(c for c in entity_cls)[:]  # Use the select query to get all entities
        return [card.to_dict() for card in entries]

    def add_record(self, entity_cls, **kwargs):
        try:
            with db_session:
                entity = entity_cls(**kwargs)
            return entity
        except Exception as e:
            raise Exception(f'Error adding record: {e}')

    def get_record_by_value(self, entity_cls, **kwargs):
        try:
            # Initialize the query with the entity class
            query = entity_cls.select()

            # Add conditions based on the key-value pairs in kwargs
            query = query.filter(**kwargs)

            # Retrieve the first matching record or None
            record = query.first()
            return record

        except Exception as e:
            print(f'Error retrieving record: {e}')
            return None

    def delete_record(self, record):
        try:
            record.delete()
        except Exception as e:
            raise Exception(f'Error deleting record: {e}')


def initialize_database():
    # Generate mapping for all entities (including Player)
    try:
        Models.generate_mapping(create_tables=True)
    except Exception as e:
        print(f'Error: {e}')
