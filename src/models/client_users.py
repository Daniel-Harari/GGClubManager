from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.sql import func
from enums import UserRole

from db import Base


class ClientUser(Base):
    __tablename__ = "client_users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password= Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at: DateTime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: DateTime = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())