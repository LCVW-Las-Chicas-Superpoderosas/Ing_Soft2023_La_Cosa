from model_base import Models
from pony.orm import PrimaryKey, Optional, Required


class Log(Models.Entity):
    id = PrimaryKey(int, auto=True)
    message = Required(str)
    created_at = Required(str)
    sent = Required(bool, default=False)
    game = Optional("Game")
