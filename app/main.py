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
from pony.orm import db_session, commit
from fastapi.middleware.cors import CORSMiddleware
import re


app = FastAPI()
app.include_router(CardsRouter)
app.include_router(GameRouter)
app.include_router(PlayerRouter)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],  # Add the origins you want to allow
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],  # Add the HTTP methods you want to allow
    allow_headers=['*']  # You can specify specific headers here or use "*" to allow any
)


@db_session
def populate_db_test():
    model_base = ModelBase()
    load_cards()
    player1 = model_base.add_record(Player, name='Gonzalo')
    player2 = model_base.add_record(Player, name='Juan')
    player3 = model_base.add_record(Player, name='Pedro')
    player4 = model_base.add_record(Player, name='Maria')
    model_base.add_record(Player, name='Lautaro')

    chat = model_base.add_record(Chat)
    # add set of players to game
    model_base.add_record(
        Game, name='Bahamas', players=[player1, player2, player3, player4],
        chats=chat, cards=model_base.get_records_by_value(Card),
        min_players=4, max_players=4, host=1)


def get_cards_from_text(text):
    result = []
    lines = text.split('\n')  # Split the text into lines
    pattern = r'(\d+)- (\s*[^\d:]+) (\d*) - (\d)'

    for line in lines:
        match = re.match(pattern, line)
        if match:
            card_id = match.group(1)
            card_name = match.group(2)
            card_number = match.group(3)
            card_type = match.group(4)
            result.append((card_id, card_name, card_type, card_number))
    return result


@db_session
def load_cards():
    model_base = ModelBase()
    with open('./app/statics/cards.txt', 'r') as f:
        cards_schema = f.read()

    cards = get_cards_from_text(cards_schema)

    for card in cards:
        model_base.add_record(Card, name=card[1],
            card_token=f'img{card[0]}.jpg', type=card[2], number=card[3])
        commit()
    model_base.add_record(Card, name='Reverse', number=None,
        card_token='reverse.jpg', type=CardType.OTHER.value)
    model_base.add_record(Card, name='Panic Reverse', number=None,
        card_token='panic-reverse.jpg', type=CardType.OTHER.value)
    print('Cards loaded successfully')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run the FastAPI application' +
        'with optional host and port parameters.')

    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host address to bind the server to.')

    parser.add_argument(
        '--port', type=int, default=8000, help='Port number to listen on.')

    parser.add_argument(
        '--test',
        type=bool,
        default=False,
        help='If True, then populate the database with some initial test data.')

    parser.add_argument(
        '--load-cards',
        type=bool,
        default=True,
        help='If True, then populate the database with the game cards.')

    args = parser.parse_args()

    try:
        initialize_database()
    except Exception as e:
        print(f'Warning: {e}')

    if args.test:
        populate_db_test()

    if args.load_cards:
        load_cards()

    uvicorn.run(app, host=args.host, port=args.port)
