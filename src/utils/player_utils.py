from typing import Iterable, Type, Union

from models import Player
from schemas.players import PlayerBase


def is_downline(username: str, downlines: Iterable[Union[Type[PlayerBase], Player]]):
    return username in [user.username for user in downlines]


