import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from crud.players import get_downlines, get_player_by_username
import crud.transactions as crud
from crud.transactions import create_transaction
from db import get_db
from gg_exceptions.auth import AuthorizationError
from utils.auth_utils import get_current_user, check_roles
from schemas.transactions import TransactionResponse, TransferTransaction
from schemas.client_users import UserRole, ClientUserResponse
from utils.player_utils import is_downline

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


@router.post("/transfer", response_model=List[TransactionResponse])
@check_roles([UserRole.MASTER, UserRole.MANAGER, UserRole.SUPER_AGENT, UserRole.AGENT])
async def transfer(transaction: TransferTransaction, current_user: ClientUserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    downlines = get_downlines(db, current_user)
    if not is_downline(transaction.transfer_from, downlines):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to transfer money from this player"
        )
    _ = get_player_by_username(db, transaction.transfer_to) # Validate player exists
    from_transaction, to_transaction = transaction.to_transaction_creates()
    from_transaction.created_by = current_user.username
    to_transaction.created_by = current_user.username
    transactions = [
        create_transaction(db, from_transaction),
        create_transaction(db, to_transaction)
    ]
    
    return transactions