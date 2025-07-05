from schemas.base import BaseSchema
from enums import UserRole
from datetime import datetime
from typing import Optional
from pydantic import Field



class PlayerRakebackSummaryBase(BaseSchema):
    username: str
    balance: float = Field(description="Current player balance")
    agent_name: Optional[str] = Field(description="Name of the player's agent")
    agent_id: Optional[str] = Field(description="ID of the player's agent")
    role: UserRole
    rake_since_last_rakeback: float = Field(description="Amount of rake generated since last rakeback payment")
    last_rakeback_date: Optional[datetime] = Field(description="Date of the last rakeback payment")
    total_rakeback_received: float = Field(description="Total lifetime rakeback payments received")
    total_lifetime_rake: float = Field(description="Total lifetime rake generated")
    total_hands_played: int = Field(description="Total number of hands played")

class PlayerRakebackSummaryResponse(PlayerRakebackSummaryBase):
    class Config:
        from_attributes = True

# Optional: Create a summary version with just the essential fields
class PlayerRakebackSimpleSummary(BaseSchema):
    username: str
    balance: float
    rake_since_last_rakeback: float
    last_rakeback_date: Optional[datetime]
    total_rakeback_received: float

    class Config:
        from_attributes = True