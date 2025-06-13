from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.sql import func
from enums import UserRole
from db import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    agent_id = Column(String, nullable=True)
    agent_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
