from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from models import Player
from models.transactions import Transaction
from utils.auth_utils import get_current_user, check_roles
from schemas.transactions import TransactionCreate, TransactionResponse
from schemas.client_users import UserRole


# Create router
router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/", response_model=TransactionResponse)
@check_roles([UserRole.MASTER, UserRole.MANAGER, UserRole.SUPER_AGENT, UserRole.AGENT])
async def create_transaction(transaction: TransactionCreate, current_user: Player = Depends(get_current_user), db: Session = Depends(get_db)):
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get('/', response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, current_user: Player = Depends(get_current_user), db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.username == current_user.username).offset(skip).limit(limit).all()
    return transactions
