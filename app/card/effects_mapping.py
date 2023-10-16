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

EFFECTS_TO_PLAYERS = {
    'lanzallamas': flame_torch,
    'vigila tus espaldas': watch_your_back
}
