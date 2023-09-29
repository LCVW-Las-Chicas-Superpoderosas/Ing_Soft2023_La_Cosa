import argparse

import uvicorn
from card.view import router as CardsRouter
from fastapi import FastAPI
from game.view import router as GameRouter
from model_base import ModelBase, initialize_database
from player.models import Player
from pony.orm import db_session

app = FastAPI()

app.include_router(CardsRouter)
app.include_router(GameRouter)


@db_session
def populate_db_test():
    model_base = ModelBase()
    model_base.add_record(Player, name='juan')
    model_base.add_record(Player, name='pedro')
    model_base.add_record(Player, name='tomi')
    model_base.add_record(Player, name='pepe')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run the FastAPI application' +
        'with optional host and port parameters.'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host address to bind the server to.',
    )
    parser.add_argument(
        '--port', type=int, default=8000, help='Port number to listen on.'
    )
    parser.add_argument(
        '--test',
        type=bool,
        default=False,
        help='If True, then populate the database with some initial test data.',
    )

    args = parser.parse_args()

    try:
        initialize_database()
    except Exception as e:
        print(f'Warning: {e}')

    if args.test is True:
        populate_db_test()

    uvicorn.run(app, host=args.host, port=args.port)
