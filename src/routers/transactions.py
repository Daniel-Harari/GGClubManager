from http.client import HTTPException
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crud.players import get_downlines, get_player_by_username
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
def get_transactions(skip: int = 0, limit: int = 100, current_user: ClientUserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.username == current_user.username).offset(skip).limit(limit).all()
    return transactions

@router.post("", response_model=TransactionResponse)
@check_roles([UserRole.MASTER, UserRole.MANAGER, UserRole.SUPER_AGENT, UserRole.AGENT])
async def create_transaction(transaction: TransactionCreate, current_user: ClientUserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    if get_player_by_username(db, transaction.username) not in get_downlines(db, current_user):
        raise HTTPException(

        )
    db_transaction = transaction.to_orm(Transaction)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
