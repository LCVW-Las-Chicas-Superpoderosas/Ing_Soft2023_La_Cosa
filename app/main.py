import argparse
import uvicorn

from card.view import router as CardsRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from game.view import router as GameRouter
from load_data import load_cards, populate_db_test
from model_base import initialize_database
from player.view import router as PlayerRouter
from ws.view import router as WsRouter


app = FastAPI()
app.include_router(CardsRouter)
app.include_router(GameRouter)
app.include_router(PlayerRouter)
app.include_router(WsRouter)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],  # Add the origins you want to allow
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],  # Add the HTTP methods you want to allow
    allow_headers=['*']  # You can specify specific headers here or use "*" to allow any
)

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
        default=False,
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
