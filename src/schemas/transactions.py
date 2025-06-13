from datetime import datetime

from pydantic import BaseModel


class TransactionBase(BaseModel):
    username: str
    re_entries: int
    fee: float
    details: str
    total_buyin: float
    total_cashout: float

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True