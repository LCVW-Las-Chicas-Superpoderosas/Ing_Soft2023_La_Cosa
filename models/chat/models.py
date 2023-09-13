from datetime import datetime

from models.model_base import Base
from sqlalchemy import Column, Integer, String, DateTime


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, index=True)  # We need to know how to make relationships
    message = Column(String, unique=True, index=True)
