from logger import GGLogger
from models import Transaction

logger = GGLogger(__name__)

def create_transaction(db, transaction):
    db.add(transaction)
    db.commit()
    logger.info(f'Created Transaction: {transaction.id}')


def get_transactions(db, username, skip: int = 0, limit: int = 100):
    transactions = db.query(Transaction).filter(Transaction.username == username).offset(skip).limit(limit).all()
    return transactions