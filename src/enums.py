from enum import Enum


class UserRole(Enum):
    MASTER = "Master"
    MANAGER = "Manager"
    SUPER_AGENT = "Super Agent"
    AGENT = "Agent"
    PLAYER = "Player"
