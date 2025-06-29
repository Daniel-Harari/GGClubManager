from logic.gg_parser import MTTDetailsDataParser, SNGDetailsDataParser, SpinAndGoldDataParser
from crud.transactions import transaction_handler
from crud.players import update_balance
from db import SessionLocal


if __name__ == '__main__':
    db = SessionLocal()
    club_id = '910171'
    parser = SpinAndGoldDataParser(club_id)
    parser.load_data_from_file()
    parser.clean_data()
    transactions = parser.get_transactions()
    for t in transactions:
        transaction_handler(db, t)
        update_balance(db, t.username, round(t.total_cashout - t.total_buyin, 2))
