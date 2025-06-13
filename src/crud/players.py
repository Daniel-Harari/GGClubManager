from typing import List

from models import Player
from schemas.client_users import ClientUserResponse
from schemas.players import PlayerResponse
from utils.player_utils import get_downline_query
from logger import  GGLogger
from gg_exceptions.players import PlayerNotFound

logger = GGLogger(__name__)

def get_player_by_username(db, username) -> PlayerResponse:
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        logger.warning(f'Player not found: {username}')
        raise PlayerNotFound
    logger.info(f'Retrieved Player: {player.username}')
    return PlayerResponse.model_validate(player)

def get_downlines(db, user: ClientUserResponse) -> List[PlayerResponse]:
    player =  get_player_by_username(db, user.username)
    downlines = db.execute(get_downline_query(player)).scalars().all()
    logger.info(f'Retrieved {len(downlines)} Downlines')
    downlines = [PlayerResponse.model_validate(player) for player in downlines]
    return downlines
