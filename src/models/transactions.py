import datetime as dt

from sqlalchemy import Column, Integer, String, Float, DateTime

from db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    re_entries = Column(Integer)
    fee = Column(Float, default=0)
    details = Column(String)
    total_buyin = Column(Float)
    total_cashout = Column(Float)
    created_at = Column(DateTime, default=dt.datetime.now(dt.UTC))
    updated_at = Column(DateTime, default=dt.datetime.now(dt.UTC), onupdate=dt.datetime.now(dt.UTC))
