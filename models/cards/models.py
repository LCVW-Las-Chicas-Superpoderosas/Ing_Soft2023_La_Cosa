from datetime import datetime

from models.model_base import Base
from sqlalchemy import Column, Integer, String, DateTime, Text


class Chat(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, unique=True, index=True)
