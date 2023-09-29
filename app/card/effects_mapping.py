from model_base import ModelBase
from player.models import Player
from pony.orm import db_session

MODEL_BASE = ModelBase()


def flame_torch(target_id):
    try:
        with db_session:
            target_user = MODEL_BASE.get_record_by_value(Player, id=target_id)
            target_user.is_alive = False
            target_user.flush()
            return True
    except Exception as e:
        print(e)
        return False


EFFECTS_TO_PLAYERS = {
    'lanzallamas': flame_torch
}
