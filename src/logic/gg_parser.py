from functools import wraps
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

import pandas as pd

from enums import UserRole
from logger import GGLogger
from schemas.players import PlayerCreate

logger = GGLogger(__name__)


def check_data_populated(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.data is None:
            raise ValueError("The 'data' attribute is not populated. Please populate it before calling this method.")
        return func(self, *args, **kwargs)
    return wrapper

class ClubGGDataParser:
    DATA_DIR = Path(__file__).parents[2] / 'resources'
    def __init__(self, club_id):
        self.club_id = club_id
        self.data: Optional[pd.DataFrame] = None

    def load_data_from_file(self, file=None, sheet_name=None, **kwargs):
        if not file:
            file = self.get_latest_file()
        logger.info(f'Getting Data From: {file}')
        self.data = pd.read_excel(file, sheet_name=sheet_name, **kwargs)

    def get_latest_file(self):
        files = self.DATA_DIR.glob(f'{self.club_id}_*.xlsx')
        latest_file = max(files, key=lambda x: x.name.split('_')[1])
        return latest_file

    @check_data_populated
    def get_total_fee_by_agent(self):
        return self.data.groupby('AGENT_NAME')['FEE'].sum().reset_index()

    def get_rakeback(self):
        df = self.get_total_fee_by_agent()
        df["RAKEBACK"] = (df.AGENT_NAME.map(self.AGENT_CUSTOM_RAKEBACK_MAPPING).fillna(self.DEFAULT_AGENT_RAKEBACK) * df.FEE).round(2)
        return df

    def get_agents_total_balance(self):
        return self.data.groupby('AGENT_NAME')['TOTAL_BALANCE'].sum().reset_index()

    def get_agents_total_balance_with_rakeback(self):
        df = self.get_agents_total_balance()
        df = df.merge(self.get_rakeback(), on='AGENT_NAME', how='left')
        df = self._calculate_overlay(df)
        adjustment = (df.loc[df.AGENT_NAME != "-", "FEE"] - df.loc[df.AGENT_NAME != "-", "RAKEBACK"]).sum()
        df.loc[df.AGENT_NAME == "-", "RAKEBACK"] += adjustment
        df['TOTAL_BALANCE_WITH_RAKEBACK'] = df.TOTAL_BALANCE + df.RAKEBACK - df.OVERLAY
        return df

    @staticmethod
    def _calculate_overlay(rakeback_df):
        rakeback_df['OVERLAY'] = 0
        overlay = (rakeback_df.TOTAL_BALANCE + rakeback_df.FEE).sum()
        rakeback_df.loc[rakeback_df.AGENT_NAME == "-", "OVERLAY"] = overlay
        return rakeback_df


class ClubOverviewDataParser(ClubGGDataParser):
    SHEET_NAME
    def __init__(self, club_id):
        super().__init__(club_id)

    def get_players(self):
        players: List[PlayerCreate] = []

        for _, row in self.data.iterrows():
            role = self._get_user_role(row.get("role"))
            if not role:
                continue

            user_id = str(row.get("id"))
            username = row.get("username")
            agent_id = row.get("agent_id")
            agent_name = row.get("agent_name")

            # Avoid self-agent for SUPER_AGENT or AGENT
            if role in {UserRole.SUPER_AGENT, UserRole.AGENT} and user_id == str(agent_id):
                agent_id = None
                agent_name = None

            player = PlayerCreate(
                id=user_id,
                username=username,
                role=role,
                agent_id=str(agent_id) if agent_id else None,
                agent_name=str(agent_name) if agent_name else None
            )
            players.append(player)

        return players

    def _get_user_role(role_str: str) -> UserRole:
        try:
            return UserRole(role_str.upper())
        except ValueError:
            return None


if __name__ == '__main__':
    parser = ClubOverviewDataParser('910171')
    parser.load_data_from_file()