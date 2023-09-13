from players.models import Player
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Add corresponding url for your database.
DATABASE_URL = "sqlite:///mydatabase.db"

# Crea una instancia de la clase base de declaraciones SQLAlchemy
Base = declarative_base()


class ModelBase:
    def __init__(self):
        # Crea la instancia de la base de datos SQLAlchemy
        self.engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)

        self.db = SessionLocal()

    def generate_tables(self):
        '''
            When you call Base.metadata.create_all(bind=engine), 
            SQLAlchemy looks at the classes that inherit from Base 
            and generates the necessary SQL statements to create the
            corresponding database table(s).
        '''
        self.Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        '''Drop all tables... BE CAREFUL!!!'''
        self.Base.metadata.drop_all(bind=self.engine)

    def add_record(self, record):
        '''Add record to the DB'''
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

    def get_record_by_id(self, model, id):
        return self.db.query(model).filter_by(id=id).first()

    # def update_record(self, record):
    #     self.db.commit()

    def delete_record(self, record):
        self.db.delete(record)
        self.db.commit()

# Ejemplo de uso:
if __name__ == "__main__":
    model_base = ModelBase()

    # Crear tabla de usuarios
    model_base.create_table()

    # Crear un nuevo usuario
    new_player = Player(username="john_doe", email="john@example.com")
    model_base.add_record(new_player)

    # Leer un usuario por ID
    user = model_base.get_record_by_id(Player, 1)
    print(user.username, user.email)

    # Modificar un usuario
    user.name = "new_username"
    model_base.update_record(user)

    # Eliminar un usuario
    model_base.delete_record(user)
