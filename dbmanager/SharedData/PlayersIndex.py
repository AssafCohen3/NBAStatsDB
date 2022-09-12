import json
from dataclasses import dataclass, field
from typing import Optional, Dict

import requests

from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc
from dbmanager.SharedData.TodayConfig import today_config
from dbmanager.constants import STATS_HEADERS, PLAYERS_INDEX_ENDPOINT

# TODO consider add bobby watson since he missing from the player index


@dataclass
class PlayerDetails:
    player_id: int
    player_name: str
    draft_year: Optional[int]
    draft_round: Optional[int]
    draft_number: Optional[int]
    first_season: int
    last_season: int
    played_games_flag: bool = field(default=False)


class PlayersIndex(SharedDataResourceAbc):
    def _fetch_data(self):
        current_season = today_config.get_current_season()
        resp = requests.get(PLAYERS_INDEX_ENDPOINT % current_season, headers=STATS_HEADERS)
        resp = json.loads(resp.text)
        players_rows = resp['resultSets'][0]['rowSet']
        players_headers = resp['resultSets'][0]['headers']
        player_id_index = players_headers.index('PERSON_ID')
        first_name_index = players_headers.index('PLAYER_FIRST_NAME')
        last_name_index = players_headers.index('PLAYER_LAST_NAME')
        draft_year_index = players_headers.index('DRAFT_YEAR')
        draft_round_index = players_headers.index('DRAFT_ROUND')
        draft_number_index = players_headers.index('DRAFT_NUMBER')
        from_year_index = players_headers.index('FROM_YEAR')
        to_year_index = players_headers.index('TO_YEAR')
        pts_index = players_headers.index('PTS')
        players = [
            PlayerDetails(
                row[player_id_index],
                row[first_name_index] + ' ' + row[last_name_index],
                int(row[draft_year_index]) if row[draft_year_index] else None,
                int(row[draft_round_index]) if row[draft_round_index] else None,
                int(row[draft_number_index]) if row[draft_number_index] else None,
                int(row[from_year_index]),
                int(row[to_year_index]),
                row[pts_index] is not None
            )
            for row in players_rows]
        to_ret: Dict[int, PlayerDetails] = {
            p.player_id: p for p in players
        }
        return to_ret

    def get_player_details(self, player_nba_id: int) -> Optional[PlayerDetails]:
        return self.get_data().get(player_nba_id)

    def is_player_played_games(self, player_nba_id: int) -> bool:
        player_details = self.get_player_details(player_nba_id)
        return player_details and player_details.played_games_flag


players_index = PlayersIndex()
