from chat.models import Chat
from fastapi import APIRouter, HTTPException
from game.models import Game, GameStatus
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


def _validate_game_creation_data(game_data: GameRequest):
    if (game_data.min_players > game_data.max_players
        or game_data.min_players < 4
            or game_data.max_players > 12):
        raise HTTPException(
            status_code=400,
            detail='Incorrect range of players.' +
            ' Please check the minimum and maximum player fields.')


def _check_player_participation(player):
    if player.game is not None:
        raise HTTPException(
            status_code=400,
            detail='User is already part of a game.')


def _player_exists(player_id):
    player = MODELBASE.get_record_by_value(Player, id=player_id)
    if player is None:
        raise HTTPException(
            status_code=400,
            detail=f'User with id {player_id} not found.')

    return player


@router.post('/game')
def create_game(game_data: GameRequest):
    _validate_game_creation_data(game_data)

    player_id = game_data.id_player
    min_players = game_data.min_players
    max_players = game_data.max_players

    with db_session:
        # Check if the player exists
        player = _player_exists(player_id)

        # Check if the player is already part of a game
        _check_player_participation(player)

        # Initialize the game
        chat = MODELBASE.add_record(Chat)
        game = MODELBASE.add_record(
            Game,
            name=game_data.name,
            password=game_data.password,
            chats=chat,
            players=player,
            min_players=min_players,
            max_players=max_players,
            host=player_id)

        return {
            'status_code': 200,
            'detail': f'Game {game.name} created successfully.',
            'data': {
                'game_id': game.id
            }
        }


class JoinGameRequest(BaseModel):
    id_game: int
    id_player: int


def _is_game_joinable(game: Game):
    # Check game status
    if game.status != GameStatus.WAITING:
        raise HTTPException(
            status_code=400,
            detail='Game is not waiting for players.')

    # Check if the game is full
    if len(game.players) >= game.max_players:
        raise HTTPException(
            status_code=400,
            detail='Game is full.')


@router.post('/game/join')
def join_game(join_game_data: JoinGameRequest):
    player_id = join_game_data.id_player
    game_id = join_game_data.id_game

    with db_session:

        # Check if the player exists
        player = _player_exists(player_id)

        # Check if the player is already part of a game
        _check_player_participation(player)

        game = MODELBASE.get_record_by_value(Game, id=game_id)

        # Check if the game exists
        if game is None:
            raise HTTPException(
                status_code=400,
                detail=f'Game with id {game_id} not found.')

        # Check game availability
        _is_game_joinable(game)

        # Add the player to the game
        player = MODELBASE.get_record_by_value(Player, id=player_id)
        game.players.add(player)

        # Return players and game host id
        players = [p.to_dict() for p in game.players]
        host = game.host
        return {
            'status_code': 200,
            'detail': f'Player {player.name} joined game {game.name} successfully.',
            'data': {
                'players': players,
                'host': host
            }
        }
