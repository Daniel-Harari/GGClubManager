from typing import Iterable, Type, Union

from models import Player
from schemas.players import PlayerBase


def get_downline(username: str, downlines: Iterable[Union[Type[PlayerBase], Player]]):
    for user in downlines:
        if user.username == username:
            return user
    return None


