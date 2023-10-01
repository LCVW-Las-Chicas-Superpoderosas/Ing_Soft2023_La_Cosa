import argparse

import uvicorn
from card.models import Card, CardType
from card.view import router as CardsRouter
from chat.models import Chat
from fastapi import FastAPI
from game.models import Game
from game.view import router as GameRouter
from model_base import ModelBase, initialize_database
from player.models import Player
from player.view import router as PlayerRouter
from pony.orm import db_session

app = FastAPI()
app.include_router(CardsRouter)
app.include_router(GameRouter)
app.include_router(PlayerRouter)


@db_session
def populate_db_test():
    model_base = ModelBase()
    card1 = model_base.add_record(
        Card, name='lanzallamas', type=CardType.PANIC.value)
    player1 = model_base.add_record(Player, name='Gonzalo')
    player2 = model_base.add_record(Player, name='Juan')
    player3 = model_base.add_record(Player, name='Pedro')
    player4 = model_base.add_record(Player, name='Maria')
    player5 = model_base.add_record(Player, name='Lautaro')

    chat = model_base.add_record(Chat)
    # add set of players to game
    game = model_base.add_record(
        Game, name='Bahamas', players=[player1, player2, player3, player4],
        chats=chat, cards=card1, min_players=4, max_players=5, host=1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run the FastAPI application' +
        'with optional host and port parameters.'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host address to bind the server to.'
    )
    parser.add_argument(
        '--port', type=int, default=8000, help='Port number to listen on.'
    )
    parser.add_argument(
        '--test',
        type=bool,
        default=False,
        help='If True, then populate the database with some initial test data.'
    )

    args = parser.parse_args()

    try:
        initialize_database()
    except Exception as e:
        print(f'Warning: {e}')

    if args.test is True:
        populate_db_test()

    uvicorn.run(app, host=args.host, port=args.port)
