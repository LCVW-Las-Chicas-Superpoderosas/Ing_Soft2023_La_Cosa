from fastapi import APIRouter, HTTPException
from model_base import ModelBase
from pony.orm import db_session, select

from model_base import ModelBase
from game.models import Game
from player.models import Player
from chat.models import Chat


from pydantic import BaseModel

router = APIRouter()
MODELBASE = ModelBase()


class GameRequest(BaseModel):
    # Modeling the request body
    id_player: int
    name: str
    password: str = ''
    min_players: int
    max_players: int


@router.post('/game')
def create_game(game_data: GameRequest):
    try:
        with db_session:
            if (
                game_data.min_players > game_data.max_players
                or game_data.min_players < 4
                or game_data.max_players > 12
            ):
                raise HTTPException(
                    status_code=400,
                    detail='Incorrect range of players. Please check the minimum and maximum player fields.',
                )

            # Check if the player is already part of a game
            player_host = MODELBASE.get_record_by_value(Player, id=game_data.id_player)
            existing_participant_game = select(
                g for g in Game if player_host in g.players
            )
            if existing_participant_game:
                raise HTTPException(
                    status_code=400, detail='User is already part of a game.'
                )

            # Not adding cards to the game for now, it is set to nullable in the model
            chat = MODELBASE.add_record(Chat)
            game = MODELBASE.add_record(
                Game,
                name=game_data.name,
                password=game_data.password,
                chats=chat,
                players=player_host,
                min_players=game_data.min_players,
                max_players=game_data.max_players,
                host=game_data.id_player,
            )

            return {
                'status_code': 200,
                'detail': f'Game {game.name} created successfully.',
                'data': {
                    'game_id': game.id,
                },
            }

    except HTTPException as http_exception:
        raise http_exception  # Re-raise HTTPExceptions to return as response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
