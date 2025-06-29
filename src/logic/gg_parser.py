from datetime import datetime
from functools import wraps
from hashlib import md5
from pathlib import Path
from typing import List, Optional, Set
import re

import pandas as pd
import numpy as np

from enums import UserRole, TransactionType
from logger import GGLogger
from schemas.players import PlayerCreate
from schemas.transactions import TransactionCreate

logger = GGLogger(__name__)


def check_data_loaded(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._raw_data is None:
            raise ValueError("The '_raw_data' attribute is not populated. Please populate it before calling this method.")
        return func(self, *args, **kwargs)
    return wrapper


def check_data_clean(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if len(self.data) == 0:
            raise ValueError("The 'data' attribute is not populated. Please populate it before calling this method.")
        return func(self, *args, **kwargs)
    return wrapper


class ClubGGDataParser:
    DATA_DIR = Path(__file__).parents[2] / 'resources'
    MULTI_TABLE_SHEET = False

    def __init__(self, club_id):
        self.club_id = club_id
        self.data: List[pd.DataFrame] = list()
        self._clean: bool = False
        self._raw_data: Optional[pd.DataFrame] = None

    def load_data_from_file(self, file=None, sheet_name=None, **kwargs):
        logger.info(sheet_name)
        if not file:
            file = self.get_latest_file()
        logger.info(f'Getting Data From: {file}')
        self._raw_data = pd.read_excel(file, sheet_name=sheet_name, header=None, **kwargs)

    def get_latest_file(self):
        files = self.DATA_DIR.glob(f'{self.club_id}_*.xlsx')
        latest_file = max(files, key=lambda x: x.name.split('_')[1])
        return latest_file

    @check_data_clean
    def _set_metadate(self, metadata_terms: Optional[Set[str]] = None, metadata_rows=1):
        for i in range(len(self.data)):
            metadata = dict()
            if metadata_terms is None:
                self.data[i].attrs = metadata
                continue

            offset = 0
            first_row = self.data[i].iloc[0]
            dt = self._get_date(first_row.iloc[0])
            if dt:
                metadata['Date'] = dt
                offset = 1
                while self._get_date(self.data[i].iloc[offset].iloc[0]):
                    offset += 1
                    metadata['Date'] = dt
            elif i > 0 and "Date" in self.data[i - 1].attrs:
                metadata['Date'] = self.data[i - 1].attrs['Date']
            for j in range(0 + offset, metadata_rows + offset):
                row = self.data[i].iloc[j]
                first_cell = str(row.iloc[0]).strip()
                if first_cell.startswith("Start/End"):
                    metadata['id'] = md5(first_cell.encode()).hexdigest()
                for term in metadata_terms:
                    if f'{term} :' in first_cell:
                        metadata[term] = first_cell.split(':')[1].split(',')[0].strip()

            self.data[i].attrs = metadata

    @staticmethod
    def _get_date(text):
        try:
            if not re.match(r'^\d{4}-\d{2}-\d{2}', str(text)):
                return None
            dt = datetime.strptime(str(text)[:10], '%Y-%m-%d')
            return dt.date()
        except (ValueError, TypeError):
            return None

    @check_data_clean
    def _set_column_names(self, columns):
        for i in range(len(self.data)):
            self.data[i].columns = columns

    @check_data_clean
    def _remove_irrelevant_rows(self, total_metadata_header_row_count: int = 1):
        for i in range(len(self.data)):
            offset = 0
            first_row = self.data[i].iloc[0]
            dt = self._get_date(first_row.iloc[0])
            if dt:
                offset=1
                while self._get_date(self.data[i].iloc[offset].iloc[0]):
                    offset += 1
            self.data[i] = self.data[i].iloc[total_metadata_header_row_count + offset:].reset_index(drop=True)

    @check_data_clean
    def keep_relevant_columns(self, column_count: int):
        for i in range(len(self.data)):
            self.data[i] = self.data[i].iloc[:, :column_count]

    @check_data_loaded
    def _split_tables(self, keyword: str = "Total"):
        if not self.MULTI_TABLE_SHEET:
            self.data = [self._raw_data]
        df = self._raw_data.iloc[:, 0]
        start_idx = 0
        for i, cell in enumerate(df):
            if keyword in str(cell):
                self.data.append(self._raw_data.iloc[start_idx:i, :])
                start_idx = i + 1

    @check_data_clean
    def _normalize_none(self):
        for i in range(len(self)):
            self.data[i] = self.data[i].replace(to_replace=["-", pd.NA, np.nan], value=None)



    def clean_data(self, columns: List[str], metadata_terms: Optional[Set[str]] = None, metadata_rows: int = 0,
                   header_rows: int = 1, *args, **kwargs):
        self._split_tables()
        self._set_metadate(metadata_terms, metadata_rows)
        self.keep_relevant_columns(len(columns))
        self._set_column_names(columns)
        self._remove_irrelevant_rows(metadata_rows + header_rows)
        self._normalize_none()
        self._clean = True
        logger.info("Finished cleaning data")

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)


class ClubOverviewDataParser(ClubGGDataParser):
    SHEET_NAME = "Club Overview"
    COLUMNS = ["Num", "SuperAgentID", "SuperAgentName", "AgentID", "AgentName", "Country", "Role", "MemberID",
               "MemberName"]
    METADATA_ROWS = 3
    METADATA_TERMS = {"Club ID", "Club Name"}
    HEADER_ROWS = 2
    MULTI_TABLE_SHEET = False

    def __init__(self, club_id):
        super().__init__(club_id)

    def load_data_from_file(self, file=None, **kwargs):
        super().load_data_from_file(file, self.SHEET_NAME, **kwargs)
        
    def clean_data(self, *args, **kwargs):
        super().clean_data(columns=self.COLUMNS, metadata_terms=self.METADATA_TERMS, metadata_rows=self.METADATA_ROWS,
                           header_rows=self.HEADER_ROWS)

    @check_data_clean
    def get_players(self):
        players: List[PlayerCreate] = []

        for _, row in self.data[0].iterrows():
            role = self._get_user_role(row["Role"])
            if not role:
                continue

            user_id = row.get("MemberID")
            username = row.get("MemberName")
            agent_id = row.get("AgentID")
            agent_name = row.get("AgentName")

            # Avoid self-agent for SUPER_AGENT or AGENT
            if role in {UserRole.SUPER_AGENT, UserRole.AGENT} and user_id == agent_id:
                agent_id = None
                agent_name = None
                if role == UserRole.AGENT:
                    agent_id = row.get("SuperAgentID")
                    agent_name = row.get("SuperAgentName")

            player = PlayerCreate(
                id=user_id,
                username=username,
                role=role,
                agent_id=agent_id,
                agent_name=agent_name,
                balance=0
            )
            players.append(player)

        return players


    @staticmethod
    def _get_user_role(role_str: str) -> Optional[UserRole]:
        try:
            return UserRole(role_str)
        except ValueError:
            return None


class SNGDetailsDataParser(ClubGGDataParser):
    SHEET_NAME = "SNG Detail"
    COLUMNS = ["MemberID", "MemberName", "Buyin", "Fee", "Hands", "Prize", "Winnings"]
    METADATA_ROWS = 3
    METADATA_TERMS = {"Table Name"}
    HEADER_ROWS = 2
    MULTI_TABLE_SHEET = True

    def __init__(self, club_id):
        super().__init__(club_id)

    def load_data_from_file(self, file=None, **kwargs):
        super().load_data_from_file(file, self.SHEET_NAME, **kwargs)

    def clean_data(self, *args, **kwargs):
        super().clean_data(columns=self.COLUMNS, metadata_terms=self.METADATA_TERMS, metadata_rows=self.METADATA_ROWS,
                           header_rows=self.HEADER_ROWS)
        
    def get_transactions(self):
        transactions: List[TransactionCreate] = list()
        for i in range(len(self)):
            df = self[i]
            for _, row in df.iterrows():
                transaction = TransactionCreate(
                    id = df.attrs['id'],
                    username=row.MemberName,
                    transaction_type=TransactionType.SNG,
                    hands=row.Hands,
                    rake=row.Fee,
                    date=df.attrs.get("Date"),
                    details=df.attrs.get("Table Name"),
                    total_buyin=row.Buyin + row.Fee,
                    total_cashout=row.Prize,
                )
                transactions.append(transaction)

        return transactions


class MTTDetailsDataParser(ClubGGDataParser):
    SHEET_NAME = "MTT Detail"
    COLUMNS = ["MemberID", "MemberName", "Buyin", "TBuyin", "Fee", "TFee", "ReBuyin", "ReTBuyin", "ReFee",
               "ReTFee", "Hands", "BountyPrize", "RegularPrize", "BubbleProtection", "Winnings"]
    METADATA_ROWS = 3
    METADATA_TERMS = {"Table Name"}
    HEADER_ROWS = 3
    MULTI_TABLE_SHEET = True

    def __init__(self, club_id):
        super().__init__(club_id)

    def load_data_from_file(self, file=None, **kwargs):
        super().load_data_from_file(file, self.SHEET_NAME, **kwargs)

    def clean_data(self, *args, **kwargs):
        super().clean_data(columns=self.COLUMNS, metadata_terms=self.METADATA_TERMS, metadata_rows=self.METADATA_ROWS,
                           header_rows=self.HEADER_ROWS)

    def get_transactions(self):
        transactions: List[TransactionCreate] = list()
        for i in range(len(self)):
            df = self[i]
            for _, row in df.iterrows():
                rake = sum([row.Fee, row.TFee, row.ReFee, row.ReTFee])
                total_buyin = sum([row.Buyin, row.TBuyin, row.ReBuyin, row.ReTBuyin, rake])
                total_cashout = round(row.Winnings + total_buyin, 2)
                transaction = TransactionCreate(
                    id=df.attrs['id'],
                    username=row.MemberName,
                    transaction_type=TransactionType.MTT,
                    rake=rake,
                    date=df.attrs.get("Date"),
                    details=df.attrs.get("Table Name", ""),
                    total_buyin=total_buyin,
                    total_cashout=total_cashout,
                    hands=row.Hands,
                )
                transactions.append(transaction)
        return transactions


class RingGameDetailsDataParser(ClubGGDataParser):
    SHEET_NAME = "Ring Game Detail"
    COLUMNS = ["MemberID", "MemberName", "Buyin", "Cashout", "Hands", "Insurance", "EVCashout", "SquidGame",
               "BadBeatFee", "BadBeatCashout", "Fee", "Total"]
    METADATA_ROWS = 3
    METADATA_TERMS = {"Table Name"}
    HEADER_ROWS = 2
    MULTI_TABLE_SHEET = True

    def __init__(self, club_id):
        super().__init__(club_id)

    def load_data_from_file(self, file=None, **kwargs):
        super().load_data_from_file(file, self.SHEET_NAME, **kwargs)

    def clean_data(self, *args, **kwargs):
        super().clean_data(columns=self.COLUMNS, metadata_terms=self.METADATA_TERMS, metadata_rows=self.METADATA_ROWS,
                           header_rows=self.HEADER_ROWS)

    def get_transactions(self):
        transactions: List[TransactionCreate] = list()
        for i in range(len(self)):
            df = self[i]
            for _, row in df.iterrows():
                transaction = TransactionCreate(
                    id=df.attrs['id'],
                    username=row.MemberName,
                    transaction_type=TransactionType.RING_GAME,
                    bad_beat_contribution=row.BadBeatFee,
                    bad_beat_cashout=row.BadBeatCashout,
                    rake=row.Fee,
                    date=df.attrs.get("Date"),
                    details=df.attrs.get("Table Name", ""),
                    total_buyin=row.Buyin,
                    total_cashout=row.Cashout,
                    hands=row.Hands
                )
                transactions.append(transaction)
        return transactions

class SpinAndGoldDataParser(ClubGGDataParser):
    SHEET_NAME = "Spin&Gold Detail"
    COLUMNS = ["MemberID", "MemberName", "Buyin", "Hands", "Prize", "Winnings"]
    METADATA_ROWS = 3
    METADATA_TERMS = {"Table Name"}
    HEADER_ROWS = 2
    MULTI_TABLE_SHEET = True

    def __init__(self, club_id):
        super().__init__(club_id)

    def load_data_from_file(self, file=None, **kwargs):
        super().load_data_from_file(file, self.SHEET_NAME, **kwargs)

    def clean_data(self, *args, **kwargs):
        super().clean_data(columns=self.COLUMNS, metadata_terms=self.METADATA_TERMS, metadata_rows=self.METADATA_ROWS,
                           header_rows=self.HEADER_ROWS)


    def get_transactions(self):
        transactions: List[TransactionCreate] = list()
        for i in range(len(self)):
            df = self[i]
            for _, row in df.iterrows():
                transaction = TransactionCreate(
                    id=df.attrs['id'],
                    username=row.MemberName,
                    transaction_type=TransactionType.SPIN_AND_GOLD,
                    date=df.attrs.get("Date"),
                    details=df.attrs.get("Table Name", ""),
                    total_buyin=row.Buyin,
                    total_cashout=row.Prize,
                    hands=row.Hands
                )
                transactions.append(transaction)
        return transactions


if __name__ == '__main__':
    parser = SNGDetailsDataParser('910171')
    parser.load_data_from_file()
    parser.clean_data()
    parser.get_transactions()
    print()

