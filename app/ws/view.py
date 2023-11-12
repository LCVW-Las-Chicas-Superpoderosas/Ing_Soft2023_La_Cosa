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
manager = ConnectionManager()


class Content(BaseModel):
    type: str = None
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

        current_player = game.players.filter(
            my_position=game.current_turn).first().id

        # Get the game status
        game_status = game.status

        if game.clockwise:
            # if current_turn is the last player, then next turn is the first player
            if game.current_turn == len(game.players) - 1:
                next_turn = 0
            else:
                next_turn = game.current_turn + 1
        else:
            if game.current_turn == 0:
                next_turn = len(game.players) - 1
            else:
                next_turn = game.current_turn - 1

        next_player = game.players.filter(
            my_position=next_turn).first().id

        await websocket.send_text(json.dumps({
            'status_code': 200,
            'detail': f'{game.name} information.',
            'data': {
                'game_status': game_status,
                'players': players,
                'current_player': current_player,
                'next_player': next_player
            }
        }))


async def play_card(request_data):
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
            return _apply_effect(user, card, target_user)
        else:
            # Send the response back to the WebSocket client
            return _apply_effect(user, card)


async def _play_card(manager, request_data, player, target, card):
    play_card_result = await play_card(request_data.content)
    play_card_result = play_card_result['data']
    await manager.send_to(
        player.id,
        data=json.dumps({
            'status_code': 200,
            'detail': 'Card played successfully defend',
            'data': {
                'type': 'play_card',
                'hand': player.get_hand(),
                'effect_result': play_card_result['effect_result'],
                'the_thing_win': play_card_result['the_thing_win'],
                'the_humans_win': play_card_result['the_humans_win']
            }
        }))
    await manager.send_to(
        target.id,
        data=json.dumps({
            'status_code': 200,
            'detail': f'Card {card.name}played successfully defend',
            'data': {
                'type': 'play_card',
                'hand': target.get_hand(),
                'effect_result': play_card_result['effect_result'],
                'the_thing_win': play_card_result['the_thing_win'],
                'the_humans_win': play_card_result['the_humans_win']
            }
        }))


# idk why but if i tried to add another router is not detected xd
@router.websocket('/ws/hand_play')
async def hand_play_endpoint(websocket: WebSocket, id_player: int):
    mb = ModelBase()

    await websocket.accept()
    manager.active_connections.append((websocket, id_player))
    try:
        while True:
            # Receive a message from the WebSocket client
            message = await websocket.receive_text()
            # Parse the incoming JSON message and validate it
            try:
                request_data = WSRequest.parse_raw(message)
            except ValidationError as validation_error:
                raise HTTPException(status_code=400, detail=validation_error.errors())

            if request_data.content.type == 'play_card':
                with db_session:
                    target = _player_exists(request_data.content.target_id)
                    player = _player_exists(id_player)

                    if not target.is_alive:
                        raise HTTPException(status_code=400, detail='Target is mad dead')
                    if not player.is_alive:
                        raise HTTPException(status_code=400, detail='Player is mad dead')

                    card = mb.get_first_record_by_value(
                        Card, card_token=request_data.content.card_token)
                    if card is None:
                        raise HTTPException(status_code=400, detail='Card not found buddy')

                    defense_cards = target.can_defend(card.name)

                    if len(defense_cards) != 0:
                        # Len not 0 aka tiene defens
                        await manager.send_to(
                            target.id,
                            data=json.dumps({
                                'status_code': 200,
                                'detail': 'Target player can defend',
                                'data': {
                                    'type': 'defense',
                                    'defense_cards': defense_cards,
                                    'attacker_id': player.id,
                                    'attacker_name': player.name,
                                    'card_being_played': card.name
                                }
                            }))
                    else:
                        player.last_card_token_played = request_data.content.card_token
                        await _play_card(manager, request_data, player, target, card)

            elif request_data.content.type == 'defense':
                with db_session:
                    player = _player_exists(id_player)
                    if not player.is_alive:
                        raise HTTPException(status_code=400, detail='Player is mad dead')

                    if request_data.content.card_token is None:
                        request_data.content.card_toke = target.last_card_token_played
                        card = mb.get_first_record_by_value(
                            Card, card_token=request_data.content.card_token)
                        if card is None:
                            raise HTTPException(status_code=400, detail='Card not found buddy')
                        _play_card(manager, request_data, target, player, card)

                    else:
                        card = mb.get_first_record_by_value(
                            Card, card_token=request_data.content.card_token)

                        if card is None:
                            raise HTTPException(status_code=400, detail='Card not found buddy')
                        if player.check_card_in_hand(card.id):
                            player.remove_card(card.id)
                            await manager.send_to(
                                id_player,
                                data=json.dumps({
                                    'status_code': 200,
                                    'detail': 'Target player defend succesfully',
                                    'data': {
                                        'type': 'defense',
                                        'hand': player.get_hand(),

                                    }}))
                        else:
                            await manager.send_to(
                                target.id,
                                data=json.dumps({
                                    'status_code': 400,
                                    'detail': 'Player doesnt have that card',
                                    'data': {
                                        'type': 'defense',
                                        'hand': target.get_hand(),
                                    }
                                }))

    except WebSocketDisconnect:
        manager.disconnect(websocket, id_player)
    except HTTPException as e:
        await websocket.send_text(
            json.dumps({
                'status_code': e.status_code,
                'detail': e.detail
            }))


@router.websocket('/ws/game_status')
async def game_status_ws(websocket: WebSocket):
    await websocket.accept()
    manager.active_connections.append((websocket, None))
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


@router.websocket('/ws/card_exchange')
async def card_exchange(websocket: WebSocket, id_player: int):
    mb = ModelBase()

    await websocket.accept()
    manager.active_connections.append((websocket, id_player))

    try:
        while True:
            message = await websocket.receive_text()
            try:
                # Parse the incoming JSON message and validate it
                request_data = WSRequest.parse_raw(message)

                if request_data.content and request_data.content.type == 'exchange_offert':
                    with db_session:
                        card = mb.get_first_record_by_value(
                            Card, card_token=request_data.content.card_token)
                        if card is None:
                            raise HTTPException(status_code=400, detail='Card not found buddy')
                        target = _player_exists(request_data.content.target_id)

                        player = _player_exists(id_player)

                        if not target.is_alive:
                            raise HTTPException(status_code=400, detail='Target is mad dead')
                        if not player.is_alive:
                            raise HTTPException(status_code=400, detail='Player is mad dead')

                        # removemos la carta que quiere dar
                        player.remove_card(card.id)
                        await manager.send_to(
                            id_player,
                            data=json.dumps({
                                'status_code': 200,
                                'detail': 'Exchange offer finished',
                                'data': {
                                    'type': 'get_result'
                                }}))
                        await manager.send_to(
                            target.id,
                            data=json.dumps({
                                'status_code': 200,
                                'detail': 'Exchange finished',
                                'data': {
                                    'type': 'get_result',
                                }}))
                        target.add_card(card)
                elif request_data.content and request_data.content.type == 'result':
                    with db_session:
                        player = _player_exists(id_player)

                        if not player.is_alive:
                            raise HTTPException(status_code=400, detail='Player is mad dead')

                        await manager.send_to(
                            id_player,
                            data=json.dumps({
                                'status_code': 200,
                                'detail': 'Result from exchange',
                                'data': {
                                    'type': 'result',
                                    'hand': player.get_hand()
                                }}))

                elif request_data.content and request_data.content.type == 'exchange':
                    with db_session:
                        card = mb.get_first_record_by_value(
                            Card, card_token=request_data.content.card_token)
                        if card is None:
                            raise HTTPException(status_code=400, detail='Card not found buddy')
                        target = _player_exists(request_data.content.target_id)

                        player = _player_exists(id_player)
                        if not target.is_alive:
                            raise HTTPException(status_code=400, detail='Target is mad dead')

                        if not player.is_alive:
                            raise HTTPException(status_code=400, detail='Player is mad dead')

                        defense = target.can_neglect_exchange()

                        if len(defense) != 0:
                            # Len not 0 aka tiene defens
                            await manager.send_to(
                                target.id,
                                data=json.dumps({
                                    'status_code': 200,
                                    'detail': 'Target player can defend',
                                    'data': {
                                        'type': 'defend',
                                        'defense_cards': defense,
                                        'attacker_id': player.id,
                                        'attacker_name': player.name
                                    }
                                }))
                        else:
                            # removemos la carta que quiere dar
                            player.remove_card(card.id)
                            await manager.send_to(
                                id_player,
                                data=json.dumps({
                                    'status_code': 200,
                                    'detail': f'Target player cant defend, exchanged card {card.id}',
                                    'data': {
                                        'type': 'exchange'
                                    }}))

                            await manager.send_to(
                                target.id,
                                data=json.dumps({
                                    'status_code': 200,
                                    'detail': 'Target player need to exchange',
                                    'data': {
                                        'type': 'exchange_offert',
                                        'attacker_id': player.id,
                                        'attacker_name': player.name

                                    }}))
                            target.add_card(card)

                elif request_data.content and request_data.content.type == 'defend':
                    with db_session:
                        player = _player_exists(id_player)
                        if not player.is_alive:
                            raise HTTPException(status_code=400, detail='Player is mad dead')

                        card = mb.get_first_record_by_value(
                            Card, card_token=request_data.content.card_token)

                        if card is None:
                            raise HTTPException(status_code=400, detail='Card not found buddy')
                        if player.check_card_in_hand(card.id):
                            player.remove_card(card.id)
                            await manager.send_to(
                                id_player,
                                data=json.dumps({
                                    'status_code': 200,
                                    'detail': 'Target player defend succesfully',
                                    'data': {
                                        'type': 'get_result',
                                    }}))
                        else:
                            await websocket.send_text(
                                json.dumps({
                                    'status_code': 400,
                                    'detail': 'Player doesnt have that card',
                                    'data': {
                                        'type': 'defend'
                                    }
                                }))

            except ValidationError as validation_error:
                await websocket.send_text(
                    json.dumps({
                        'status_code': 400,
                        'detail': validation_error.errors()
                    }))

    except WebSocketDisconnect:
        manager.disconnect(websocket, id_player)

    except HTTPException as e:
        await websocket.send_text(
            json.dumps({
                'status_code': e.status_code,
                'detail': e.detail
            }))
