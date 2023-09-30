from chat.models import Chat
from fastapi import APIRouter, HTTPException
from game.models import Game
from model_base import ModelBase
from player.models import Player
from pony.orm import db_session
from pydantic import BaseModel

router = APIRouter()
MODELBASE = ModelBase()


class GameRequest(BaseModel):
    # Modeling the request body
    id_player: int
    name: str
    # password is optional and Null by default
    password: str = None
    min_players: int
    max_players: int


def validate_game_creation_data(game_data: GameRequest):
    if (game_data.min_players > game_data.max_players or
    game_data.min_players < 4 or game_data.max_players > 12):
        raise HTTPException(
            status_code=400,
            detail='Incorrect range of players. ' +
            'Please check the minimum and maximum player fields.')


def check_player_participation(id_player):
    player = MODELBASE.get_first_record_by_value(Player, id=id_player)
    existing_participant_game = player.game
    if existing_participant_game is not None:
        raise HTTPException(
            status_code=400,
            detail='User is already part of a game.')


@router.post('/game')
def create_game(game_data: GameRequest):

    validate_game_creation_data(game_data)

    with db_session:
        check_player_participation(game_data.id_player)

    with db_session:
        try:
            player = MODELBASE.get_first_record_by_value(
                Player, id=game_data.id_player)
            chat = MODELBASE.add_record(Chat)
            game = MODELBASE.add_record(
                Game,
                name=game_data.name,
                password=game_data.password,
                chats=chat,
                players=player,
                min_players=game_data.min_players,
                max_players=game_data.max_players,
                host=game_data.id_player,
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e))
    return {
        'status_code': 200,
        'detail': f'Game {game.name} created successfully.',
        'data': {
            'game_id': game.id,
        }
    }
