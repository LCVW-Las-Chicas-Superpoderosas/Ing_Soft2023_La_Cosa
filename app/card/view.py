from card.effects_mapping import EFFECTS_TO_PLAYERS
from card.models import Card
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import HTTPException
from game.models import Game, GameStatus
from model_base import ModelBase
from player.models import Player
from model_base import ConnectionManager
from pony.orm import db_session
from pydantic import BaseModel, ValidationError
import json

router = APIRouter()
MODEL_BASE = ModelBase()


class PlayCardRequest(BaseModel):
    ''' Model The JSON Request Body '''
    action: str
    card_token: str
    id_player: int
    target_id: int = None  # Default value is None


# make target_user optional and None by default
def _apply_effect(user, card, target_user = None):
    # Check if the card is in the user's hand
    if card not in user.cards:
        raise HTTPException(status_code=400, detail=f"Card {card.name} is not in the user's hand")

    # Check that the users are in the same game:
    if target_user is not None:
        if user.game != target_user.game:
            raise HTTPException(status_code=400, detail='Users are not in the same game')

    # Get the game that contains the players
    game = MODEL_BASE.get_first_record_by_value(Game, id=user.game.id)

    # Check if the game contains these players
    if game is None:
        raise HTTPException(status_code=400,
            detail='Game not found for these players')

    # Remove the card from the user that played it
    user.cards.remove(card)

    # Apply the card effect
    effect = EFFECTS_TO_PLAYERS.get((card.name.lower()))

    if effect is None:
        raise HTTPException(status_code=400, detail=f'Card {card.name} effect not found')

    # If the effect is not specific to a target user, apply it to the user who played the card
    if target_user is None:
        effect_status = effect(user.id)
    else:
        effect_status = effect(target_user.id)

    if effect_status is False:
        raise HTTPException(status_code=400, detail=f'Card {card.name} effect failed')

    # Update the entities
    game.flush()
    user.flush()

    # Return the updated data
    user_data = user.to_dict()
    target_data = target_user.to_dict() if target_user else None

    return {
        'status_code': 200,
        'detail': f'Card {card.name} played successfully',
        'data': {
            'user': user_data,
            'target_user': target_data,
            'the_thing_win': game.validate_the_thing_win(),
            'the_humans_win': game.validate_humans_win()
        }
    }



@router.websocket('/hand/play/')
async def websocket_endpoint(websocket: WebSocket, request_body: PlayCardRequest):
    manager = ConnectionManager()
    await websocket.accept()

    try:
        while True:
            # Receive a message from the WebSocket client
            message = await websocket.receive_text()

            # Parse the incoming JSON message
            try:
                request_data = PlayCardRequest.parse_raw(message)
            except ValidationError:
                raise HTTPException(status_code=400, detail="Invalid JSON format")

            # You should define a message format that includes the required data.
            # For example, you can send a JSON message like:
            # {"action": "play_card", "card_token": "your_card_token", "id_player": 123, "target_id": 456}
            request_data = json.loads(message)

            if request_data["action"] == "play_card":

                card_token = request_data['card_token']
                id_player = request_data['id_player']
                target_id = request_data['target_id']

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

                    if not user.game.check_turn(user.my_position):
                        raise HTTPException(status_code=400, detail=f'It is not {user.name} turn')

                    if target_id >= 0:
                        target_user = MODEL_BASE.get_first_record_by_value(
                            Player, id=target_id)
                        if target_user is None:
                            raise HTTPException(status_code=400, detail='Target user not found')

                    # Send the response back to the WebSocket client
                        await websocket.send_json(_apply_effect(user, card, target_user))
                    else:
                        # Send the response back to the WebSocket client
                        await websocket.send_json(_apply_effect(user, card))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(HTTPException(status_code=400, detail='Target user not found'))
    except HTTPException as e:
        manager.disconnect(websocket)
        await manager.broadcast(e)
