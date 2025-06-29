from datetime import datetime, date
from hashlib import md5
from typing import Optional

from enums import TransactionType
from schemas.base import BaseSchema

class TransactionBase(BaseSchema):
    id: str
    username: str
    transaction_type: TransactionType
    details: str
    total_buyin: float
    total_cashout: float
    date: Optional[date]

class TransactionCreate(TransactionBase):
    rake: float = 0
    bad_beat_contribution: float = 0
    bad_beat_cashout: float = 0
    hands: int = 0

class TransactionResponse(TransactionBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransferTransaction:
    transfer_to: str
    transfer_amount: float
    date: date = date.today()



    def to_transaction_create(self,) -> TransactionCreate:
        return TransactionCreate(
            id=md5(str(datetime.now()).encode()).hexdigest(),
            username=self.transfer_to,
            transaction_type=TransactionType.TRANSFER,
            details=f'Transfer to {self.transfer_to}',
            total_buyin=0,
            total_cashout=self.transfer_amount,
            date=date.today()
        )