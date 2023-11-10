from card.models import Card
from card.view import _apply_effect, router
from fastapi import WebSocket, WebSocketDisconnect
from fastapi import HTTPException
from game.models import GameStatus
from model_base import ModelBase
from player.models import Player
from model_base import ConnectionManager
from pony.orm import db_session
from pydantic import BaseModel, ValidationError
import json
from game.view import _player_exists
import asyncio

MODEL_BASE = ModelBase()


class Content(BaseModel):
    card_token: str = None
    id_player: int = None
    target_id: int = None  # Default value is None
    # agregar chat_message y message


class WSRequest(BaseModel):
    ''' Model The JSON Request Body '''
    content: Content = None


async def get_game_info(websocket, request_data):
    # You can access specific headers by their names
    id_player = request_data.id_player

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

        await websocket.send_text(json.dumps({
            'status_code': 200,
            'detail': f'{game.name} information.',
            'data': {
                'game_status': game_status,
                'players': players,
                'current_player': current_player
            }
        }))


async def play_card(websocket, request_data):
    card_token = request_data.card_token
    id_player = request_data.id_player
    target_id = request_data.target_id

    with db_session:
        card = MODEL_BASE.get_first_record_by_value(Card, card_token=card_token)
        # Check if the card exists
        if card is None:
            raise HTTPException(status_code=400, detail=f'Card token: {card_token} not found')
        user = MODEL_BASE.get_first_record_by_value(Player, id=id_player)

        # Check if the user exists
        if user is None:
            raise HTTPException(status_code=400, detail=f'User {id_player} not found')

        if not user.is_alive:
            raise HTTPException(status_code=400, detail=f'User {user.name} is dead')

        if user.game.status != GameStatus.STARTED.value:
            raise HTTPException(status_code=400, detail=f'Game {user.game.name} is not in progress')

        if target_id is not None and target_id >= 0:
            target_user = MODEL_BASE.get_first_record_by_value(Player, id=target_id)
            if target_user is None:
                raise HTTPException(status_code=400, detail='Target user not found')

            # Send the response back to the WebSocket client
            await websocket.send_text(json.dumps(_apply_effect(user, card, target_user)))
        else:
            # Send the response back to the WebSocket client
            await websocket.send_text(json.dumps(_apply_effect(user, card)))


# idk why but if i tried to add another router is not detected xd
@router.websocket('/ws/hand_play')
async def websocket_endpoint(websocket: WebSocket):
    manager = ConnectionManager()

    await websocket.accept()
    manager.active_connections.append(websocket)

    try:
        while True:
            # Receive a message from the WebSocket client
            message = await websocket.receive_text()

            # Parse the incoming JSON message and validate it
            try:
                request_data = WSRequest.parse_raw(message)
            except ValidationError as validation_error:
                raise HTTPException(status_code=400, detail=validation_error.errors())

            await play_card(websocket, request_data.content)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except HTTPException as e:
        await websocket.send_text(
            json.dumps({
                'status_code': e.status_code,
                'detail': e.detail
            }))


# idk why but if i tried to add another router is not detected xd
@router.websocket('/ws/game_status')
async def game_status_ws(websocket: WebSocket):
    manager = ConnectionManager()
    await websocket.accept()
    manager.active_connections.append(websocket)
    request_data = None
    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=3)  # Set a timeout of 3 seconds
                try:
                    # Parse the incoming JSON message and validate it
                    request_data = WSRequest.parse_raw(message)
                    await get_game_info(websocket, request_data.content)
                except ValidationError as validation_error:
                    await websocket.send_text(
                        json.dumps({
                            'status_code': 400,
                            'detail': validation_error.errors()
                        }))
            except asyncio.TimeoutError:
                if request_data is not None:
                    await get_game_info(websocket, request_data.content)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except HTTPException as e:
        await websocket.send_text(
            json.dumps({
                'status_code': e.status_code,
                'detail': e.detail
            }))
