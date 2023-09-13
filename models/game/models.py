from datetime import datetime

from models.model_base import Base
from sqlalchemy import Column, Integer, String, DateTime


class Game(Base):
    __tablename__ = "game"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
