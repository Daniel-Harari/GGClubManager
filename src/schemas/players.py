from datetime import datetime
from typing import Optional
from enums import UserRole
from schemas.base import BaseSchema

class PlayerBase(BaseSchema):
    username: str
    agent_id: Optional[str]
    agent_name: Optional[str]
    role: UserRole
    balance: float

class PlayerCreate(PlayerBase):
    id: str

    class Config:
        from_attributes = True

class PlayerResponse(PlayerCreate):
    created_at: datetime
    updated_at: datetime

