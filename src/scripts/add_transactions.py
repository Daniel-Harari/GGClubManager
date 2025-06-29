from logic.gg_parser import MTTDetailsDataParser
from crud.transactions import create_transaction
from crud.players import update_balance
from db import SessionLocal
from models import Transaction

if __name__ == '__main__':
    db = SessionLocal()
    club_id = '910171'
    parser = MTTDetailsDataParser(club_id)
    parser.load_data_from_file()
    parser.clean_data()
    transactions = parser.get_transactions()
    for t in transactions:
        transaction = t.to_orm(Transaction)
        create_transaction(db, transaction)
        update_balance(db, t.username, round(t.total_cashout - t.total_buyin, 2))
