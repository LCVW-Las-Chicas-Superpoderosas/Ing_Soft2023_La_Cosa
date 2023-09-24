from fastapi import APIRouter
from model_base import ModelBase
from pony.orm import db_session

from model_base import ModelBase
from game.models import Game
from player.models import Player
from card.models import Card
from chat.models import Chat
from card.models import CardType


from pydantic import BaseModel


router = APIRouter()
MODELBASE = ModelBase()


# datos que llegan en la solicitud POST
class GameRequest(BaseModel):
    name: str
    password: str = ''


@router.post('/game')
def create_game(game_data: GameRequest):
    with db_session:
        chat = MODELBASE.add_record(Chat)  # chat de la sala de juego, ignorar por ahora
        player = MODELBASE.add_record(
            Player, name='Lauta'
        )  # jugador que crea la sala de juego
        card = MODELBASE.add_record(
            Card, name='Lauta_card', type=CardType.PANIC.value
        )  # carta que se le asigna al jugador que crea la sala de juego
        game = MODELBASE.add_record(
            Game,
            name=game_data.name,
            password=game_data.password,
            chats=chat,
            cards=card,
            players=player,
        )

    # devolver un mensaje de éxito con el nombre de la sala de juego
    return {'detail', f'La sala de juego: {game.name} ha sido creada exitosamente.'}
