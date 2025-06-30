import datetime as dt

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum
from enums import TransactionType
from db import Base


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, primary_key=True, index=True)
    transaction_type = Column(Enum(TransactionType), index=True)
    details = Column(String)
    total_buyin = Column(Float)
    total_cashout = Column(Float)
    date = Column(Date, nullable=True)
    rake = Column(Float, default=0)
    bad_beat_contribution = Column(Float, default=0)
    bad_beat_cashout = Column(Float, default=0)
    hands = Column(Integer, default=0)
    created_by = Column(String)
    created_at = Column(DateTime, default=dt.datetime.now(dt.UTC))
    updated_at = Column(DateTime, default=dt.datetime.now(dt.UTC), onupdate=dt.datetime.now(dt.UTC))
