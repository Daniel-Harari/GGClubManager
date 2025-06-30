import datetime
from http.client import HTTPException
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crud.players import get_downlines, get_player_by_username
import crud.transactions as crud
from db import get_db
from models.transactions import Transaction
from utils.auth_utils import get_current_user, check_roles
from schemas.transactions import TransactionCreate, TransactionResponse
from schemas.client_users import UserRole, ClientUserResponse


# Create router
router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.get('', response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, from_date: datetime.date = None, to_date: datetime.date = None,
                     current_user: ClientUserResponse = Depends(get_current_user), db: Session = Depends(get_db)):

    return crud.get_transactions(db, username=current_user.username, skip=skip, limit=limit, from_date=from_date,
                                 to_date=to_date)


@router.post("/transfer", response_model=TransactionResponse)
@check_roles([UserRole.MASTER, UserRole.MANAGER, UserRole.SUPER_AGENT, UserRole.AGENT])
async def transfer(transaction: TransactionCreate, current_user: ClientUserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    if get_player_by_username(db, transaction.username) not in get_downlines(db, current_user):
        raise HTTPException(

        )
    return crud.create_transaction(db, transaction)
