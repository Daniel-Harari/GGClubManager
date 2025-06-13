from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from crud.players import get_downlines
from schemas.players import PlayerResponse
from schemas.client_users import ClientUserResponse
from utils.auth_utils import get_current_user

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.get("/downlines", response_model=List[PlayerResponse])
def player_downlines(
        current_user: ClientUserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    downlines = get_downlines(db, current_user)

    return downlines
