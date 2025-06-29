import datetime as dt

from sqlalchemy import Column, Integer, String, Float, DateTime, Date

from db import Base


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    details = Column(String)
    total_buyin = Column(Float)
    total_cashout = Column(Float)
    date = Column(Date, nullable=True)
    rake = Column(Float, default=0)
    bad_beat_contribution = Column(Float, default=0)
    bad_beat_cashout = Column(Float, default=0)
    hands = Column(Integer, default=0)

    created_at = Column(DateTime, default=dt.datetime.now(dt.UTC))
    updated_at = Column(DateTime, default=dt.datetime.now(dt.UTC), onupdate=dt.datetime.now(dt.UTC))
