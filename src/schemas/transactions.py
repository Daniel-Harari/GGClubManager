from datetime import datetime, date
from typing import Optional

from schemas.base import BaseSchema

class TransactionBase(BaseSchema):
    username: str
    details: str
    total_buyin: float
    total_cashout: float
    date: Optional[date]

class TransactionCreate(TransactionBase):
    rake: int = 0
    bad_beat_contribution: float = 0
    bad_beat_cashout: float = 0
    hands: int = 0


class TransactionResponse(TransactionBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True