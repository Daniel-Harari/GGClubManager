from enum import Enum


class UserRole(Enum):
    MASTER = "Master"
    MANAGER = "Manager"
    SUPER_AGENT = "Super Agent"
    AGENT = "Agent"
    PLAYER = "Player"


class TransactionType(Enum):
    MTT = "MTT"
    SNG = "SnG"
    RING_GAME = "Ring Game"
    SPIN_AND_GOLD = "Spin and Gold"
    LEADERBOARD = "Leaderboard"
    TRANSFER = "Transfer"