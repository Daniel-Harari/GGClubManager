from sqlalchemy import select, or_

from schemas.players import PlayerResponse
from models.players import Player
from enums import UserRole



def get_downline_query(player: PlayerResponse):
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
