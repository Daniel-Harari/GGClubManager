from fastapi import HTTPException
from crud.players import update_balance
from logger import GGLogger
from models import Transaction
from schemas.transactions import TransactionCreate
from datetime import date
from typing import Optional, Sequence
from sqlalchemy import select

logger = GGLogger(__name__)


def create_transaction(db, transaction: TransactionCreate):
    transaction = transaction.to_orm(Transaction)
    try:
        db.add(transaction)
        db.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Transaction already exists")
    update_balance(db, transaction.username, round(transaction.total_cashout - transaction.total_buyin, 2))
    logger.info(f'Created Transaction: {transaction.id}')
    return transaction


def get_transactions(
    db, 
    username: str, 
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0, 
    limit: int = 100
) -> Sequence[Transaction]:
    """
    Get transactions for a user with optional date range filtering.
    
    Args:
        db: Database session
        username: Username to filter transactions
        from_date: Start date (inclusive)
        to_date: End date (inclusive)
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    query = select(Transaction).where(Transaction.username == username)
    
    if from_date:
        query = query.where(Transaction.date >= from_date)
    
    if to_date:
        query = query.where(Transaction.date <= to_date)
        
    return db.execute(query.offset(skip).limit(limit)).scalars().all()


def get_transaction(db, id, username) -> Transaction:
    transaction = db.query(Transaction).filter(Transaction.id == id, Transaction.username == username).first()
    return transaction


def overwrite_transaction(db, transaction: TransactionCreate):
    db_transaction = get_transaction(db, transaction.id, transaction.username)
    if db_transaction:
        # Fields to check and update
        fields = [
            'total_buyin',
            'total_cashout',
            'rake',
            'bad_beat_contribution',
            'bad_beat_cashout',
            'hands'
        ]
        original_profit = db_transaction.total_cashout - db_transaction.total_buyin
        
        # Track if any changes were made

        if transaction.hands > db_transaction.hands:
            for field in fields:
                new_value = getattr(transaction, field)
                current_value = getattr(db_transaction, field)
                if current_value != new_value:
                    setattr(db_transaction, field, new_value)

            db.commit()
            logger.info(f'Updated Transaction: {transaction.id}')
            new_profit = db_transaction.total_cashout - db_transaction.total_buyin
            update_balance(db, transaction.username, float(round(new_profit - original_profit, 2)))
    else:
        create_transaction(db, transaction)
