from logic.gg_parser import MTTDetailsDataParser, SNGDetailsDataParser, SpinAndGoldDataParser, RingGameDetailsDataParser
from crud.transactions import overwrite_transaction
from db import SessionLocal


if __name__ == '__main__':
    db = SessionLocal()
    club_id = '910171'
    for parser_cls in [SNGDetailsDataParser, MTTDetailsDataParser, SpinAndGoldDataParser, RingGameDetailsDataParser]:
        parser = parser_cls(club_id)
        parser.load_data_from_file()
        parser.clean_data()
        transactions = parser.get_transactions()
        for t in transactions:
            overwrite_transaction(db, t)
