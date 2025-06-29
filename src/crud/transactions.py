from enums import TransactionType
from logger import GGLogger
from models import Transaction
from schemas.transactions import TransactionCreate

logger = GGLogger(__name__)

def create_transaction(db, transaction: TransactionCreate):
    db.add(transaction.to_orm(Transaction))
    db.commit()
    logger.info(f'Created Transaction: {transaction.id}')


def get_transactions(db, username, skip: int = 0, limit: int = 100) -> list[Transaction]:
    transactions = db.query(Transaction).filter(Transaction.username == username).offset(skip).limit(limit).all()
    return transactions

def get_transaction(db, id, username) -> Transaction:
    transaction = db.query(Transaction).filter(Transaction.id == id, Transaction.username == username).first()
    return transaction

def merge_transaction(db, transaction: TransactionCreate):
    db_transaction = get_transaction(db, transaction.id, transaction.username)
    if db_transaction:
        db_transaction.total_buyin += transaction.total_buyin
        db_transaction.total_cashout += transaction.total_cashout
        db_transaction.rake += transaction.rake
        db_transaction.bad_beat_contribution += transaction.bad_beat_contribution
        db_transaction.bad_beat_cashout += transaction.bad_beat_cashout
        db_transaction.hands += transaction.hands
        db.commit()
    else:
        create_transaction(db, transaction)
    logger.info(f'Updated Transaction: {transaction.id}')

def overwrite_transaction(db, transaction: TransactionCreate):
    db_transaction = get_transaction(db, transaction.id, transaction.username)
    if db_transaction:
        db_transaction.total_buyin = transaction.total_buyin
        db_transaction.total_cashout = transaction.total_cashout
        db_transaction.rake = transaction.rake
        db_transaction.bad_beat_contribution = transaction.bad_beat_contribution
        db_transaction.bad_beat_cashout = transaction.bad_beat_cashout
        db_transaction.hands = transaction.hands
        db.commit()
        logger.info(f'Updated Transaction: {transaction.id}')
    else:
        create_transaction(db, transaction)

def transaction_handler(db, transaction: TransactionCreate):
    match transaction.transaction_type:
        case TransactionType.RING_GAME:
            merge_transaction(db, transaction)
        case TransactionType.MTT | TransactionType.SNG | TransactionType.SPIN_AND_GOLD:
            overwrite_transaction(db, transaction)
