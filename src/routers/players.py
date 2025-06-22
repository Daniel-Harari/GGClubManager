from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
import crud.players as player_crud
from enums import UserRole
from gg_exceptions.players import PlayerNotFound
from schemas.players import PlayerResponse, PlayerCreate
from schemas.client_users import ClientUserResponse
from utils.auth_utils import get_current_user, check_roles


router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.get("", response_model=PlayerResponse)
@check_roles([UserRole.MASTER, UserRole.MANAGER])
async def get_player(player_name: str, db: Session = Depends(get_db), current_user: ClientUserResponse = Depends(get_current_user)):
    return player_crud.get_player_by_username(db, player_name)

@router.post("", response_model=PlayerResponse)
@check_roles([UserRole.MASTER, UserRole.MANAGER])
async def create_player(player: PlayerCreate, db: Session = Depends(get_db), current_user: ClientUserResponse = Depends(get_current_user)):
    return player_crud.create_player(db, player)

@router.put("", response_model=PlayerResponse)
@check_roles([UserRole.MASTER, UserRole.MANAGER])
async def update_player(player: PlayerCreate, db: Session = Depends(get_db), current_user: ClientUserResponse = Depends(get_current_user)):
    player_crud.update_player(db, player)

@router.get("/downlines", response_model=List[PlayerResponse])
@check_roles([UserRole.MASTER, UserRole.MANAGER, UserRole.SUPER_AGENT, UserRole.AGENT])
async def player_downlines(current_user: ClientUserResponse = Depends(get_current_user),db: Session = Depends(get_db)):
    downlines = player_crud.get_downlines(db, current_user)

    return downlines

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
