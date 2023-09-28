import argparse

from card.models import Card, CardType
from card.view import router as CardsRouter
from player.view import router as PlayerRouter
from chat.models import Chat
from fastapi import FastAPI
from game.models import Game
from model_base import initialize_database, ModelBase
from player.models import Player
from pony.orm import db_session
import uvicorn

app = FastAPI()

app.include_router(CardsRouter)
app.include_router(PlayerRouter)


@db_session
def populate_db_test():
    model_base = ModelBase()
    player = model_base.add_record(Player, name='el_pepe_test')
    card = model_base.add_record(Card, name='el_pepe_card2', type=CardType.PANIC.value)
    chat = model_base.add_record(Chat)
    model_base.add_record(Game, name='el_pepe_game2', password='', chats=chat, cards=card, players=player)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the FastAPI application with optional host and port parameters.')
    parser.add_argument('--host', type=str, default='localhost', help='Host address to bind the server to.')
    parser.add_argument('--port', type=int, default=8000, help='Port number to listen on.')
    parser.add_argument('--test', type=bool, default=False, help='If True, then populate the database with some initial test data.')

    args = parser.parse_args()

    try:
        initialize_database()
    except Exception as e:
        print(f'Warning: {e}')

    if args.test is True:
        populate_db_test()

    uvicorn.run(app, host=args.host, port=args.port)
