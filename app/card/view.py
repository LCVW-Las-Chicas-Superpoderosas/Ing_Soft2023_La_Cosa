from card.effects_mapping import EFFECTS_TO_PLAYERS
from card.models import Card
from fastapi import APIRouter
from fastapi import HTTPException
from game.models import Game
from model_base import ModelBase
from player.models import Player
from pony.orm import db_session
from pydantic import BaseModel


router = APIRouter()
MODEL_BASE = ModelBase()


class PlayCardRequest(BaseModel):
    ''' Model The JSON Request Body '''
    card_token: str
    id_usuario: int
    target_id: int = None  # Default value is None


def _targeted_effect(target_user, card, user):
    # Check if the card is in the user's hand
    if card not in user.cards:
        raise HTTPException(status_code=400, detail=f"Card {card.name} is not in the user's hand")

    # Check that the users are in the same game:
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
            user.name: user_data,
            target_user.name: target_data
        }
    }


@router.post('/hand/play/')
def play_card(request_body: PlayCardRequest):
    card_token = request_body.card_token
    id_usuario = request_body.id_usuario
    target_id = request_body.target_id

    with db_session:

        card = MODEL_BASE.get_first_record_by_value(Card, card_token=card_token)

        # Check if the card exists
        if card is None:
            raise HTTPException(status_code=400, detail=f'Card token: {card_token} not found')
        user = MODEL_BASE.get_first_record_by_value(Player, id=id_usuario)

        # Check if the user exists
        if user is None:
            raise HTTPException(status_code=400, detail=f'User {id_usuario} not found')
        if not user.is_alive:
            raise HTTPException(status_code=400, detail=f'User {user.name} is dead')
        if target_id is not None:
            target_user = MODEL_BASE.get_first_record_by_value(
                Player, id=target_id)
            if target_user is None:
                raise HTTPException(status_code=400, detail='Target user not found')

            return _targeted_effect(target_user, card, user)
