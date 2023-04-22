import csv
import datetime
import os.path
from dataclasses import dataclass
from typing import List, Optional, Dict
from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc
from dbmanager.utils import get_application_path


@dataclass
class DefaultPlayerMapping:
    player_nba_id: int
    player_nba_name: str
    player_nba_birthdate: Optional[datetime.date]
    player_bref_id: str
    player_bref_name: str
    player_bref_birthdate: Optional[datetime.date]

    def to_list(self):
        return [
            self.player_nba_id,
            self.player_nba_name,
            self.player_nba_birthdate,
            self.player_bref_id,
            self.player_bref_name,
            self.player_bref_birthdate
        ]


class DefaultMappings(SharedDataResourceAbc[Dict[int, DefaultPlayerMapping]]):
    def _fetch_data(self):
        mappings: List[DefaultPlayerMapping] = []
        file_path = get_application_path() / 'dbmanager/players_ids/players.csv'
        with open(file_path, encoding='ISO-8859-1') as f:
            csvreader = csv.reader(f, )
            headers = next(csvreader)
            bref_id_idx = headers.index('PlayerBREFId')
            bref_name_idx = headers.index('PlayerBREFName')
            bref_birthdate_idx = headers.index('PlayerBREFBirthDate')
            nba_id_idx = headers.index('PlayerNBAId')
            nba_name_idx = headers.index('PlayerNBAName')
            nba_birthdate_idx = headers.index('PlayerNBABirthDate')
            for p in csvreader:
                mappings.append(DefaultPlayerMapping(
                    int(p[nba_id_idx]),
                    p[nba_name_idx],
                    datetime.date.fromisoformat(p[nba_birthdate_idx]) if p[nba_birthdate_idx] != '' else None,
                    p[bref_id_idx],
                    p[bref_name_idx],
                    datetime.date.fromisoformat(p[bref_birthdate_idx]) if p[bref_birthdate_idx] != '' else None,
                ))
        return {
            m.player_nba_id: m for m in mappings
            # for testing
            # if m.player_nba_id not in [1630532, 1627863]
        }

    def get_player_mapping(self, player_nba_id: int) -> Optional[DefaultPlayerMapping]:
        return self.get_data().get(player_nba_id)


default_mappings = DefaultMappings()
