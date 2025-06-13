from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enums import UserRole

class PlayerBase(BaseModel):
    username: str
    agent_id: Optional[str]
    agent_name: Optional[str]
    role: UserRole

class PlayerCreate(PlayerBase):
    id: str

    class Config:
        from_attributes = True

class PlayerResponse(PlayerCreate):
    created_at: datetime
    updated_at: datetime

