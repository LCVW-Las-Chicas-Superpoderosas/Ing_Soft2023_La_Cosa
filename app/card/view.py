from card.effects_mapping import EFFECTS_TO_PLAYERS
from card.models import Card
from fastapi import APIRouter
from fastapi import HTTPException
from game.models import Game, GameStatus
from model_base import ModelBase
from player.models import Player
from pony.orm import db_session
from pydantic import BaseModel

router = APIRouter()
MODEL_BASE = ModelBase()


class PlayCardRequest(BaseModel):
    ''' Model The JSON Request Body '''
    card_token: str
    id_player: int
    target_id: int = None  # Default value is None


# make target_user optional and None by default
def _apply_effect(user, card, target_user=None):
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
        effect_result = effect(user.id)
    else:
        effect_result = effect(target_user.id)

    if effect_result['status'] is False:
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
            'the_humans_win': game.validate_humans_win(),
            'effect_data': effect_result.get('data', None)
        }
    }


def _validate_play(card_token, id_player, target_id):
    user = MODEL_BASE.get_first_record_by_value(Player, id=id_player)
    clockwise = user.game.clockwise
    adjascent_players = user.game.get_adjascent_players()
    left_player = adjascent_players[0]
    right_player = adjascent_players[1]

    # extract number from card token string, e.g., img48.jpg -> 48
    card_token = int(card_token[3:-4])


    '''
    [22, 26]: flame torch
    [27, 29]: analysis
    [32, 39]: suspicion
    ''' 
    if  22 <= card_token <= 39:
        if target_id not in adjascent_players:
            raise HTTPException(status_code=400, detail='Target user is not adjacent to the user')

    '''
    [67, 70]: scary
    [74, 77]: no, thanks!
    [78, 80]: you failed! 
    '''
    if (67 <= card_token <= 70) or (74 <= card_token <= 80):
        if (clockwise and target_id != left_player) or (not clockwise and target_id != right_player):
            raise HTTPException(status_code=400, detail='Target user should be the next player in the turn')

    '''
    [40, 42]: whisky
    [48, 49]: watch your back
    '''
    if (40 <= card_token <= 42) or (48 <= card_token <= 49):
        if target_id >= 0:
            # "the player itself" means the card is supposed to be played on the user who played it
            # OR its a global effect
            raise HTTPException(status_code=400, detail='Target user is not the player itself')



@router.post('/hand/play/')
def play_card(request_body: PlayCardRequest):
    card_token = request_body.card_token
    id_player = request_body.id_player
    target_id = request_body.target_id

    with db_session:
        
        _validate_play(card_token, id_player, target_id)

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

            return _apply_effect(user, card, target_user)

        else:
            return _apply_effect(user, card)
