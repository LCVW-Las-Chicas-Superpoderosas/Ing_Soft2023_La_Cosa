import asyncio
import json
from datetime import datetime

from card.models import Card
from card.view import _apply_effect, router
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from game.models import GameStatus
from game.view import _player_exists
from model_base import ConnectionManager, ModelBase
from player.models import Player
from pony.orm import db_session, commit
from pydantic import BaseModel, ValidationError

MODEL_BASE = ModelBase()
manager = ConnectionManager()
chatManager = ConnectionManager()


class Content(BaseModel):
    type: str = None
    card_token: str = None
    id_player: int = None
    target_id: int = None  # Default value is None
    chat_message: str = None
    do_defense: bool = 0


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


async def play_card(user, target_user, card):
    with db_session:

        # Check if the user exists
        if user is None:
            raise HTTPException(status_code=400, detail=f'Player not found')

        if not user.is_alive:
            raise HTTPException(status_code=400, detail=f'User {user.name} is dead')

        if user.game.status != GameStatus.STARTED.value:
            raise HTTPException(status_code=400, detail=f'Game {user.game.name} is not in progress')

        if target_user is not None:
            # Send the response back to the WebSocket client
            return _apply_effect(user, card, target_user)
        else:
            # Send the response back to the WebSocket client
            return _apply_effect(user, card)


async def manage_play_card(manager, player, target, card):
    play_card_result = await play_card(player, target, card)
    play_card_result = play_card_result['data']
    await manager.send_to(
        player.id,
        data=json.dumps({
            'status_code': 200,
            'detail': 'Card played successfully',
            'data': {
                'type': 'play_card',
                'hand': player.get_hand(),
                'the_thing_win': play_card_result['the_thing_win'],
                'the_humans_win': play_card_result['the_humans_win'],
                'effect_data': play_card_result['effect_data']
            }
        }))
    if player is not None:
        await manager.send_to(
            target.id,
            data=json.dumps({
                'status_code': 200,
                'detail': f'Card {card.name}played successfully',
                'data': {
                    'type': 'play_card',
                    'hand': target.get_hand(),
                    'the_thing_win': play_card_result['the_thing_win'],
                    'the_humans_win': play_card_result['the_humans_win'],
                    'effect_data': play_card_result['effect_data']
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
                if request_data.content.target_id < 0:
                    request_data.content.target_id = None
            except ValidationError as validation_error:
                raise HTTPException(status_code=400, detail=validation_error.errors())

            if request_data.content.type == 'play_card':
                with db_session:
                    player = _player_exists(id_player)
                    if not player.is_alive:
                        raise HTTPException(status_code=400, detail='Player is mad dead')

                    card = mb.get_first_record_by_value(
                        Card, card_token=request_data.content.card_token)
                    if card is None:
                        raise HTTPException(status_code=400, detail='Card not found, buddy')

                    player.last_card_token_played = request_data.content.card_token

                    if request_data.content.target_id is not None:
                        target = _player_exists(request_data.content.target_id)

                        if not target.is_alive:
                            raise HTTPException(status_code=400, detail='Target is mad dead')

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
                                        'card_being_played': card.name,
                                        'under_attack': True
                                    }
                                }))
                        else:
                            is_exchange = card.is_exchange()
                            if is_exchange:
                                # removemos la carta que quiere dar ya que no se pudo defender
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

                            else:
                                await manage_play_card(manager, player, target, card)
                    else:
                        player.last_card_token_played = request_data.content.card_token
                        await manage_play_card(manager, player, None, card)

            elif request_data.content.type == 'defense':
                with db_session:
                    player = _player_exists(id_player)
                    if not player.is_alive:
                        raise HTTPException(status_code=400, detail='Player is mad dead')

                    target = _player_exists(request_data.content.target_id)             
                    if not target.is_alive:
                        raise HTTPException(status_code=400, detail='Target is mad dead')

                    if request_data.content.do_defense:
                        card = mb.get_first_record_by_value(
                            Card, card_token=request_data.content.card_token)
                        if card is None:
                            raise HTTPException(status_code=400, detail='Card not found buddy')

                        player.remove_card(card.id)
                        if player.check_card_in_hand(card.id):
                            await manager.send_to(
                                id_player,
                                data=json.dumps({
                                    'status_code': 200,
                                    'detail': 'Player defend succesfully',
                                    'data': {
                                        'type': 'defense',
                                        'hand': player.get_hand(),
                                        'under_attack': False
                                    }}))
                            await manager.send_to(
                                target.id,

                                data=json.dumps({
                                    'status_code': 200,
                                    'detail': 'Target player defend succesfully',
                                    'data': {
                                        'type': 'defense',
                                        'hand': target.get_hand(),
                                        'under_attack': False
                                    }}))
                        else:
                            await manager.send_to(
                                id_player,
                                data=json.dumps({
                                    'status_code': 400,
                                    'detail': 'Player doesnt have that card',
                                    'data': {
                                        'type': 'defense',
                                        'hand': player.get_hand(),
                                        'under_attack': False
                                    }
                                }))
                    else:
                        card = mb.get_first_record_by_value(
                            Card, card_token=target.last_card_token_played)
                        if card is None:
                            raise HTTPException(status_code=400, detail='Card not found buddy')
                        await manage_play_card(manager, target, player, card)

            elif request_data.content and request_data.content.type == 'exchange_offert':
                with db_session:
                    target = _player_exists(request_data.content.target_id)
                    if not target.is_alive:
                        raise HTTPException(status_code=400, detail='Target is mad dead')

                    player = _player_exists(id_player)
                    if not player.is_alive:
                        raise HTTPException(status_code=400, detail='Player is mad dead')

                    card = mb.get_first_record_by_value(
                        Card, card_token=request_data.content.card_token)
                    if card is None:
                        raise HTTPException(status_code=400, detail='Card not found buddy')

                    # removemos la carta que quiere dar
                    player.remove_card(card.id)
                    target.add_card(card)
                    commit()

                    await manager.send_to(
                        id_player,
                        data=json.dumps({
                            'status_code': 200,
                            'detail': 'Result from exchange',
                            'data': {
                                'type': 'result',
                                'hand': player.get_hand()
                            }}))
                    await manager.send_to(
                        target.id,
                        data=json.dumps({
                            'status_code': 200,
                            'detail': 'Result from exchange',
                            'data': {
                                'type': 'result',
                                'hand': target.get_hand()
                            }}))
    except WebSocketDisconnect:
        await manager.disconnect(websocket, id_player)
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
                        target.add_card(card)
                        commit()

                        await manager.send_to(
                            id_player,
                            data=json.dumps({
                                'status_code': 200,
                                'detail': 'Result from exchange',
                                'data': {
                                    'type': 'result',
                                    'hand': player.get_hand()
                                }}))
                        await manager.send_to(
                            target.id,
                            data=json.dumps({
                                'status_code': 200,
                                'detail': 'Result from exchange',
                                'data': {
                                    'type': 'result',
                                    'hand': target.get_hand()
                                }}))

                elif request_data.content and request_data.content.type == 'exchange':
                    with db_session:
                        card = mb.get_first_record_by_value(
                            Card, card_token=request_data.content.card_token)
                        if card is None:
                            raise HTTPException(status_code=400, detail='Card not found buddy')

                        target = _player_exists(request_data.content.target_id)
                        if not target.is_alive:
                            raise HTTPException(status_code=400, detail='Target is mad dead')

                        player = _player_exists(id_player)
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
                            target.add_card(card)
                            commit()
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

                elif request_data.content and request_data.content.type == 'defend':
                    with db_session:
                        player = _player_exists(id_player)
                        if not player.is_alive:
                            raise HTTPException(status_code=400, detail='Player is mad dead')

                        target = _player_exists(request_data.content.target_id)
                        if not target.is_alive:
                            raise HTTPException(status_code=400, detail='Target is mad dead')

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
                                    'detail': 'Result from exchange',
                                    'data': {
                                        'type': 'result',
                                        'hand': player.get_hand()
                                    }}))
                            await manager.send_to(
                                target.id,
                                data=json.dumps({
                                    'status_code': 200,
                                    'detail': 'Result from exchange',
                                    'data': {
                                        'type': 'result',
                                        'hand': target.get_hand()
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
        await manager.disconnect(websocket, id_player)

    except HTTPException as e:
        await websocket.send_text(
            json.dumps({
                'status_code': e.status_code,
                'detail': e.detail
            }))
        

async def broadcast_chat_message(request_data):
    chat_message = request_data.chat_message
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

        # If the message is empty, don't send it
        if chat_message == '':
            raise HTTPException(
                status_code=400,
                detail='Message is empty.')

        chat_message = f'[{datetime.now().strftime("%H:%M:%S")}] {player.name}: {chat_message}'

        for connection, conn_id in chatManager.active_connections:
            await connection.send_text(json.dumps({
                'status_code': 200,
                'detail': 'New message received',
                'data': {
                    'type': 'chat_message',
                    'message': chat_message
                }
            }))    



@router.websocket('/ws/chat')
async def chat_endpoint(websocket: WebSocket, id_player: int):
    await websocket.accept()
    chatManager.active_connections.append((websocket, id_player))
    request_data = None
    try:
        while True:
            try:
                # use asyncio to wait for the message
                message = await asyncio.wait_for(websocket.receive_text(), timeout=1100) 
                try:
                    # Parse the incoming JSON message and validate it
                    request_data = WSRequest.parse_raw(message)
                    if request_data.content.type == 'chat_message':
                        await broadcast_chat_message(request_data.content)
                except ValidationError as validation_error:
                    await websocket.send_text(
                        json.dumps({
                            'status_code': 400,
                            'detail': validation_error.errors()
                        }))
            except asyncio.TimeoutError:
                if request_data is not None:
                    await broadcast_chat_message(request_data.content)
                else:
                    await websocket.send_text(
                        json.dumps({
                            'status_code': 400,
                            'detail': 'Message could not be sent.'
                        }))

    except WebSocketDisconnect:
        await chatManager.disconnect(websocket, id_player)
    except HTTPException as e:
        await websocket.send_text(
            json.dumps({
                'status_code': e.status_code,
                'detail': e.detail
            }))
