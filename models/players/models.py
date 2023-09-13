from datetime import datetime

from models.model_base import Base
from sqlalchemy import Column, Integer, String, DateTime


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
