from logic.gg_parser import ClubOverviewDataParser
from crud.players import update_player
from db import SessionLocal


if __name__ == '__main__':
    db = SessionLocal()
    club_id = '910171'
    parser = ClubOverviewDataParser(club_id)
    parser.load_data_from_file()
    parser.clean_data()
    players = parser.get_players()
    for player in players:
        update_player(db, player)