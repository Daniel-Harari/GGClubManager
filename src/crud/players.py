from typing import Sequence, Type

from sqlalchemy.orm import Session

from schemas.client_users import ClientUserResponse
from logger import  GGLogger
from gg_exceptions.players import PlayerNotFound
from sqlalchemy import select, or_

from schemas.players import PlayerCreate
from models.players import Player
from enums import UserRole



logger = GGLogger(__name__)

def create_player(db: Session, player: PlayerCreate) -> Type[Player]:
    player = player.to_orm(Player)
    db.add(player)
    db.commit()
    logger.info(f'Created Player: {player.username}')
    return player


def update_player(db: Session, player: PlayerCreate) -> Type[Player]:
    """
    Update player if there are differences between current and new values.
    Returns updated player or None if player not found.
    """
    # Get existing player
    try:
        db_player = get_player_by_username(db, player.username)
    except PlayerNotFound:
        return create_player(db, player)

    # Convert update data to dict, excluding None values
    update_data = player.model_dump(exclude_unset=True)

    # Track if any changes were made
    has_changes = False

    # Update only if values are different
    for field, new_value in update_data.items():
        current_value = getattr(db_player, field)
        if current_value != new_value:
            setattr(db_player, field, new_value)
            has_changes = True

    # Commit only if there were changes
    if has_changes:
        db.commit()

    return db_player


def get_player_by_username(db: Session, username) -> Type[Player]:
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        logger.warning(f'Player not found: {username}')
        raise PlayerNotFound
    logger.info(f'Retrieved Player: {player.username}')
    return player

def get_downlines(db: Session, user: ClientUserResponse) -> Sequence[Player]:
    player =  get_player_by_username(db, user.username)

    downlines = db.execute(get_downline_query(player)).scalars().all()
    logger.info(f'Retrieved {len(downlines)} Downlines')
    return downlines

def get_downline_query(player: Type[Player]):
    query = select(Player)

    if player.role in [UserRole.MASTER, UserRole.MANAGER]:
        # Master and Manager can see all users except other Masters and Managers
        query = query.where(Player.role.notin_([UserRole.MASTER, UserRole.MANAGER]))

    elif player.role == UserRole.SUPER_AGENT:
        query = query.where(
            or_(
                # Direct Agents
                (player.role == UserRole.AGENT) & (player.agent_id == player.id),
                # Players under those Agents
                (Player.role == UserRole.PLAYER) & (
                    Player.agent_id.in_(
                        select(Player.id).where(
                            (Player.role == UserRole.AGENT) &
                            (Player.agent_id == player.id)
                        )
                    )
                )
            )
        )

    elif player.role == UserRole.AGENT:
        query = query.where(
            (Player.role == UserRole.PLAYER) &
            (Player.agent_id == player.id)
        )

    return query

def update_balance(db: Session, username: str, amount: float):
    if username == 'DaniDonk':
        print('DaniDonk')
    player = get_player_by_username(db, username)
    player.balance += amount
    db.commit()