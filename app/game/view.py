import json
import random

from card.models import Card
from chat.models import Chat
from fastapi import APIRouter, Header, HTTPException
from game.models import Game, GameStatus
from model_base import ModelBase
from player.models import Player
from pony.orm import commit, db_session
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


class NextTurnRequest(BaseModel):
    # Modeling the request body
    game_id: int


class JoinGameRequest(BaseModel):
    id_game: int
    id_player: int


class GameStartRequest(BaseModel):
    id_player: int


class GameDeleteRequest(BaseModel):
    id_game: int


class DiscardCardRequest(BaseModel):
    id_player: int
    card_token: str


class HandRequest(BaseModel):
    id_player: int


def _validate_game_creation_data(game_data: GameRequest):
    if (game_data.min_players > game_data.max_players or
            game_data.min_players < 4 or game_data.max_players > 12):
        raise HTTPException(
            status_code=400,
            detail='Incorrect range of players. ' +
            'Please check the minimum and maximum player fields.')


def _check_player_participation(player):
    if player.game is not None:
        raise HTTPException(
            status_code=400,
            detail='User is already part of a game.')


def _player_exists(player_id):
    player = MODELBASE.get_first_record_by_value(Player, id=player_id)
    if player is None:
        raise HTTPException(
            status_code=400,
            detail=f'User with id {player_id} not found.')

    return player


@router.post('/game/next_turn')
def next_turn(game_data: NextTurnRequest):
    with db_session:
        game = MODELBASE.get_first_record_by_value(Game, id=game_data.game_id)

        if game is None:
            raise HTTPException(status_code=400, detail='Game not found.')

        try:
            current_turn = game.next_turn()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        player_turn = game.players.filter(my_position=current_turn)

        if player_turn is None:
            # This is most not likely to happend... buuut
            raise HTTPException(status_code=500, detail='InternalError: the ' +
                'player with next turn is not in this game!. better call saul')

        player_turn = player_turn.first()

    return {
        'status_code': 200,
        'detail': f'Next turn for game {game.name} set successfully.',
        'data': {
            'current_turn': current_turn,
            'player_id': player_turn.id
        }
    }


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

        game.set_turns()

    return {
        'status_code': 200,
        'detail': f'Game {game.name} created successfully.',
        'data': {
            'game_id': game.id
        }
    }


def _is_game_joinable(game: Game):
    # Check game status
    if game.status != GameStatus.WAITING.value:
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

        game = MODELBASE.get_first_record_by_value(Game, id=game_id)

        # Check if the game exists
        if game is None:
            raise HTTPException(
                status_code=400,
                detail=f'Game with id {game_id} not found.')

        # Check game availability
        _is_game_joinable(game)

        # Add the player to the game
        player = MODELBASE.get_first_record_by_value(Player, id=player_id)
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


def _is_game_startable(game: Game):
    # Check game status and number of players
    # return true if game can be started
    return (game.status == GameStatus.WAITING.value and
        len(game.players) >= game.min_players)


@router.get('/game/join')
def lobby_info(id_player: int = Header(..., key='id-player')):

    with db_session:
        # Check if the player exists
        player = _player_exists(id_player)

        # Get the game
        game = player.game

        # If player is not part of a game, return error
        if game is None:
            raise HTTPException(
                status_code=400,
                detail='Player is not part of a game.')

        # Check if game can be started
        can_start = _is_game_startable(game)

        players = [p.to_dict() for p in game.players]
        is_host = game.host == id_player
        return {
            'status_code': 200,
            'detail': f'{game.name} lobby information.',
            'data': {
                'players': players,
                'game_status': game.status,
                'is_host': is_host,
                'can_start': can_start
            }
        }


@router.put('/game/start')
def start_game(game_data: GameStartRequest):
    id_player = game_data.id_player

    with db_session:
        # Check if the player exists
        player = _player_exists(id_player)

        # Get the game
        game = player.game

        # If player is not part of a game, return error
        if game is None:
            raise HTTPException(
                status_code=400,
                detail='Player is not part of a game.')

        # Check if player is the host
        if game.host != id_player:
            raise HTTPException(
                status_code=400,
                detail='Only the host can start the game.')

        # Check if game can be started
        if not _is_game_startable(game):
            raise HTTPException(
                status_code=400,
                detail='Game cannot be started.')

        # Set turns
        current_turn = game.set_turns()

        player_turn = game.players.filter(my_position=current_turn)

        if player_turn is None:
            # This is most not likely to happend... buuut
            raise HTTPException(status_code=500, detail='InternalError: the ' +
                'player with next turn is not in this game!. better call saul')

        # Give cards to users
        game.initial_repartition_of_cards()

        players_hands = {}
        for player in game.players:
            players_hands[player.id] = {
                'cards': [{'card_token': card.card_token, 'type': card.type}
                    for card in player.cards]
            }

        # Set game status
        game.status = GameStatus.STARTED.value

        # Return OK
        return {
            'status_code': 200,
            'detail': f'Game {game.name} started successfully.',
            'data': {
                'player_hands': players_hands,
                'player_id': player_turn.first().id
            },
        }


@router.delete('/game')
def delete_game(game_data: GameDeleteRequest):
    with db_session:
        game = MODELBASE.get_first_record_by_value(Game, id=game_data.id_game)
        if game is None:
            raise HTTPException(status_code=400, detail='Game not found.')
        game.clean_game()
        game.delete()
    return {
        'status_code': 200,
        'detail': 'Game deleted successfully.',
        'data': {}
    }


@router.get('/hand')
def player_hand(id_player: int = Header(..., key='id-player')):
    with db_session:

        player = MODELBASE.get_first_record_by_value(
            Player, id=id_player)

        if player.game is None:
            raise HTTPException(
                status_code=400,
                detail=f'Player {player.name}, id: {player.id} is not in game'
            )

        if player.game.status == 0:  # 0 = WAITING
            raise HTTPException(
                status_code=400,
                detail=f'The game is not started, cannot get hand of {player.id}'
            )

        if player.game.status == 2:  # 2 = FINISHED
            raise HTTPException(
                status_code=400,
                detail=f'The game is finished, cannot get hand of {player.id}'
            )

        hand = [{'card_token': card.card_token, 'type': card.type}
            for card in player.cards]

    return {
        'status_code': 200,
        'message': f'Player {player.name} id:{player.id} hand',
        'data': {
            'hand': hand
        }
    }


@router.put('/hand')
def put_hand(hand_request: HandRequest):
    id_player = hand_request.id_player
    with db_session:

        player = MODELBASE.get_first_record_by_value(Player, id=id_player)

        if player.game is None:
            raise HTTPException(
                status_code=400,
                detail=f'Player {player.name}, id: {player.id} is not in game'
            )

        if player.game.status == 0:  # 0 = WAITING
            raise HTTPException(
                status_code=400,
                detail='The game is not started, cannot get card from deck'
            )

        if player.game.status == 2:  # 2 = FINISHED
            raise HTTPException(
                status_code=400,
                detail='The game is finished, cannot get card from deck'
            )

        # Get card from deck
        if player.game.next_card_in_deck() is None:
            sort_discard_pile = player.game.get_discard_pile()
            random.shuffle(sort_discard_pile)

            player.game.deck = json.dumps(sort_discard_pile)

        card = player.game.next_card_in_deck()
        player.game.delete_first_card_in_deck()

        # Card from deck (Still a list bc Endpoint Contract)
        picked_cards = []
        picked_cards.append({
            'card_token': card.card_token,
            'type': card.type
        })

        player.cards.add(card)

        # Get next_card_type
        if player.game.next_card_in_deck() is None:
            sort_discard_pile = player.game.get_discard_pile()
            random.shuffle(sort_discard_pile)
            player.game.deck = sort_discard_pile

        next_card = player.game.next_card_in_deck()
        next_card_type = next_card.type
        commit()

    return {
        'status_code': 200,
        'message': f'Succesfully retrieved cards from deck for {player.name},id:{player.id}',
        'data': {
            'picked_cards': picked_cards,
            'next_card_type': next_card_type
        }
    }


@router.get('/game/list')
def get_games_list():
    with db_session:
        games = MODELBASE.get_records_by_value(Game)
        games_list = []

        for game in games:
            if (game.status == GameStatus.WAITING.value and
                    len(game.players) < game.max_players):
                games_list.append({
                    'game_id': game.id,
                    'player_quantity': game.players.count(),
                    'max_players': game.max_players,
                    'name': game.name
                })

        return {
            'status_code': 200,
            'detail': 'Joinable games list.',
            'data': games_list
        }


@router.get('/game')
def get_game_info(id_player: int = Header(..., key='id-player')):

    with db_session:
        # Check if the player exists
        player = _player_exists(id_player)

        # Get the game
        game = player.game

        # If player is not part of a game, return error
        if game is None:
            raise HTTPException(
                status_code=400,
                detail='Player is not part of a game.')

        # Check if game is waiting for players
        # if it is, return error
        if game.status == GameStatus.WAITING.value:
            raise HTTPException(
                status_code=400,
                detail='Game is waiting for players. Cannot get game info.')

        # Get players, return a list of dicts that contain the player:
        # name, id, position, is_alive
        players = []

        for player in game.players:
            players.append({
                'name': player.name,
                'id': player.id,
                'position': player.my_position,
                'is_alive': player.is_alive
            })

        # Get the current turn player id
        current_player = game.players.filter(
            my_position=game.current_turn).first().id

        # Get the game status
        game_status = game.status

        return {
            'status_code': 200,
            'detail': f'{game.name} information.',
            'data': {
                'game_status': game_status,
                'players': players,
                'current_player': current_player
            }
        }


@router.delete('/game/join')
def leave_game(id_player: int = Header(..., key='id-player')):
    with db_session:
        # Check if the player exists
        player = _player_exists(id_player)
        game = player.game

        if game is None:
            raise HTTPException(
                status_code=400,
                detail='The player is not in a game')

        if game.status != GameStatus.WAITING.value:
            raise HTTPException(
                status_code=400,
                detail='Cant leave a game if the player is not in the lobby')

        try:
            if player.id == player.game.host:
                player.game.clean_game()
            else:
                player.leave_game()
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=e)

        return {
            'status_code': 200,
            'detail': f'{player.name} Leave the game succesfulrly. '
            '(if game_status=2, all players have been wiped out, if is 0, only the player leave)',
            'data': {
                'game_status': game.status
            }
        }


@router.post('/game/discard_card')
def discard_card(data: DiscardCardRequest):
    player_id = data.id_player
    card_token = data.card_token

    with db_session:
        # Check if the player exists
        player = _player_exists(player_id)

        card_id = MODELBASE.get_first_record_by_value(
            Card, card_token=card_token).id

        if not player.check_card_in_hand(card_id):
            raise HTTPException(
                status_code=400,
                detail=f'Card with {card_id} not in player({player_id}) hand.'
            )

        game = player.game
        if game is None:
            raise HTTPException(
                status_code=400,
                detail=f'player({player_id}) is not playing any game...'
            )

        if game.status != GameStatus.STARTED.value:
            raise HTTPException(
                status_code=400,
                detail='Game is not started.')

        game.add_card_to_discard_pile(card_id)

        try:
            player.remove_card(card_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

        hand = [{
            'card_token': card.card_token,
            'type': card.type} for card in player.cards]

    return {
        'status_code': 200,
        'message':
            f'Player {player.name} id:{player.id} ' +
            'discard card sucessfully',
        'data': {'hand': hand}
    }
