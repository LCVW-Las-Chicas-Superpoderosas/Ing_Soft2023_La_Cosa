from card.models import Card
from fastapi import APIRouter
from model_base import ModelBase
from pony.orm import db_session

router = APIRouter()
MODEL_BASE = ModelBase()


@router.get("/cards/get_all_cards")
def get_all_cards():
    with db_session:
        cards = MODEL_BASE.get_all_entry_of_entity(Card)
    return {"cards": cards}


@router.get("/cards/get_card/{card_token}")
async def get_card(card_token: str):
    with db_session:
        card_filter = {"card_token": card_token}
        cards = MODEL_BASE.get_record_by_value(Card, card_filter)
    return {"cards": cards}
