
from sqlalchemy import Column, String, Float, DateTime, Integer
from db import Base


class PlayerRakebackSummary(Base):
    __tablename__ = "player_rakeback_summary"
    
    username = Column(String, primary_key=True)
    balance = Column(Float)
    agent_name = Column(String)
    agent_id = Column(String)
    role = Column(String)
    rake_since_last_rakeback = Column(Float)
    last_rakeback_date = Column(DateTime, nullable=True)
    total_rakeback_received = Column(Float)
    total_lifetime_rake = Column(Float)
    total_hands_played = Column(Integer)

    # Make this a view
    __table_args__ = {'extend_existing': True}
