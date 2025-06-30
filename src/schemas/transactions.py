from datetime import datetime, date
from hashlib import md5
from typing import Optional, Tuple

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
    created_by: str

class TransactionResponse(TransactionBase):
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransferTransaction:
    transfer_from: str
    transfer_to: str
    transfer_amount: float
    date: date = date.today()


    def to_transaction_creates(self,) -> Tuple[TransactionCreate, TransactionCreate]:
        return (TransactionCreate(
            id=md5(f'{self.transfer_from}-{self.transfer_to}-{self.transfer_amount}-{self.date}'.encode()).hexdigest(),
            username=self.transfer_to,
            transaction_type=TransactionType.TRANSFER,
            details=f'Transfer to {self.transfer_to}',
            total_buyin=0,
            total_cashout=self.transfer_amount,
            date=date.today()
        ),

        TransactionCreate(
            id=md5(f'{self.transfer_from}-{self.transfer_to}-{self.transfer_amount}-{self.date}'.encode()).hexdigest(),
            username=self.transfer_from,
            transaction_type=TransactionType.TRANSFER,
            details=f'Transfer from {self.transfer_from}',
            total_buyin=self.transfer_amount,
            total_cashout=0,
        ))