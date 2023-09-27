from player.models import Player
from fastapi import APIRouter
from model_base import ModelBase
from pony.orm import db_session
from pydantic import BaseModel
from fastapi import HTTPException

router = APIRouter()
MODEL_BASE = ModelBase()


class RegisterRequest(BaseModel):
    name: str


@router.post('/register')
def register_player(request_body: RegisterRequest):
    try:
        with db_session:
            new_player = MODEL_BASE.add_record(Player, name=request_body.name)
            new_player_data = new_player.to_dict()

        return {
            'status_code': 200,
            'detail': f'User {new_player.name} registered successfully',
            'data': new_player_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
