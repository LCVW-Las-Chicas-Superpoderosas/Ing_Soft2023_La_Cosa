from model_base import ModelBase
from player.models import Player
from pony.orm import db_session

MODEL_BASE = ModelBase()


def flame_torch(target_id):
    try:
        with db_session:
            target_user = MODEL_BASE.get_first_record_by_value(Player, id=target_id)
            target_user.is_alive = False
            target_user.flush()
            return True
    except Exception as e:
        print(e)
        return False


# "watch_your_back" is a card that sets Game.clockwise to False
def watch_your_back(player_id):
    try:
        with db_session:
            player = MODEL_BASE.get_first_record_by_value(Player, id=player_id)
            game = player.game
            game.clockwise = not game.clockwise
            game.flush()
            return True
    except Exception as e:
        print(e)
        return False


def swap_places(target_id):
    try:
        with db_session:

            # get target
            target = MODEL_BASE.get_first_record_by_value(Player, id=target_id)

            # get game
            game = target.game

            # get player who played the swap
            player_turn = game.current_turn
            player = MODEL_BASE.get_first_record_by_value(Player, my_position=player_turn)

            # swap
            target_position = target.my_position
            target.my_position = player.my_position
            player.my_position = target_position

            # set the current_turn to the player that played the car
            # so it can finish the turn
            game.current_turn = player.my_position

            target.flush()
            player.flush()
            game.flush()
            return True
    except Exception as e:
        print(e)
        return False


EFFECTS_TO_PLAYERS = {
    'lanzallamas': flame_torch,
    'vigila tus espaldas': watch_your_back,
    'cambio de lugar!': swap_places
}
