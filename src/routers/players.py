from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
import crud.players as player_crud
from enums import UserRole
from gg_exceptions.players import PlayerNotFound
from schemas.players import PlayerResponse, PlayerCreate
from schemas.client_users import ClientUserResponse
from utils.auth_utils import get_current_user, check_roles
from utils.player_utils import get_downline

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.get("", response_model=PlayerResponse)
async def get_current_player(current_user: ClientUserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return player_crud.get_player_by_username(db, current_user.username)


@router.post("", response_model=PlayerResponse)
@check_roles([UserRole.MASTER, UserRole.MANAGER])
async def create_player(player: PlayerCreate, db: Session = Depends(get_db), current_user: ClientUserResponse = Depends(get_current_user)):
    return player_crud.create_player(db, player)


@router.put("", response_model=PlayerResponse)
@check_roles([UserRole.MASTER, UserRole.MANAGER])
async def update_player(player: PlayerCreate, db: Session = Depends(get_db), current_user: ClientUserResponse = Depends(get_current_user)):
    player_crud.update_player(db, player)


@router.delete("", response_model=None)
@check_roles([UserRole.MASTER, UserRole.MANAGER])
async def delete_player(username: str, db: Session = Depends(get_db), current_user: ClientUserResponse = Depends(get_current_user)):
    try:
        player = player_crud.get_player_by_username(db, username)
        db.delete(player)
        db.commit()

    except PlayerNotFound:
        raise
    return None


@router.get("/downlines", response_model=List[PlayerResponse])
@check_roles([UserRole.MASTER, UserRole.MANAGER, UserRole.SUPER_AGENT, UserRole.AGENT])
async def player_downlines(current_user: ClientUserResponse = Depends(get_current_user),db: Session = Depends(get_db)):
    return player_crud.get_downlines(db, current_user)


@router.get("/{player_username}", response_model=PlayerResponse)
@check_roles([UserRole.MASTER, UserRole.MANAGER, UserRole.SUPER_AGENT, UserRole.AGENT])
async def get_player(player_username: str, db: Session = Depends(get_db), current_user: ClientUserResponse = Depends(get_current_user)):
    downlines = player_crud.get_downlines(db, current_user)
    player = get_downline(player_username, downlines)
    if not player:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this player's information"
        )
    return player
