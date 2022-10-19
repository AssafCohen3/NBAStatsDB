import datetime
import json
from builtins import staticmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

import requests

from dbmanager.SeasonType import SeasonType, PLAYOFFS_SEASON_TYPE
from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc
from dbmanager.constants import STATS_HEADERS, BOXSCORES_ENDPOINT, STATS_API_COUNT_THRESHOLD, \
    NBA_GAME_IDS_GAME_DATE_CORRECTION

EXCLUDED_MATCHUPS_DATES: List[str] = [
    '1954-03-16',
    '1954-03-17',
    '1954-03-18',
    '1954-03-20',
    '1954-03-21',
    '1954-03-22',
]


@dataclass
class ScheduleGame:
    team_a_id: int = field(init=False, default=0)
    team_b_id: int = field(init=False, default=0)
    game_id: str

    def append_team(self, team_id):
        if self.team_a_id != 0 and self.team_b_id != 0:
            raise Exception('how')
        if self.team_a_id == 0 or self.team_a_id > team_id:
            self.team_b_id = self.team_a_id
            self.team_a_id = team_id
        else:
            self.team_b_id = team_id


@dataclass
class ScheduleMatchup:
    season: int
    team_a_id: int
    team_b_id: int
    start_date: str = field(init=False, default='')
    end_date: str = field(init=False, default='')

    def append_game_date(self, game_date: str):
        if self.start_date == '' or self.start_date > game_date:
            self.start_date = game_date
        if self.end_date == '' or self.end_date < game_date:
            self.end_date = game_date


@dataclass
class ScheduleSeason:
    season: int
    dates: Dict[str, Dict[str, ScheduleGame]] = field(init=False, default_factory=dict)

    def append_game(self, game_date, game_id, team_id):
        if game_date not in self.dates:
            self.dates[game_date] = {}
        if game_id not in self.dates[game_date]:
            self.dates[game_date][game_id] = ScheduleGame(game_id)
        self.dates[game_date][game_id].append_team(team_id)

    def get_mathcups(self) -> List[ScheduleMatchup]:
        to_ret: Dict[Tuple[int, int], ScheduleMatchup] = {}
        for game_date, date_games in self.dates.items():
            if game_date in EXCLUDED_MATCHUPS_DATES:
                continue
            for game in date_games.values():
                if (game.team_a_id, game.team_b_id) not in to_ret:
                    to_ret[(game.team_a_id, game.team_b_id)] = ScheduleMatchup(self.season, game.team_a_id, game.team_b_id)
                to_ret[(game.team_a_id, game.team_b_id)].append_game_date(game_date)
        return list(to_ret.values())


@dataclass
class Schedule:
    seasons: Dict[int, ScheduleSeason] = field(init=False, default_factory=dict)

    def append_game(self, season, game_date, game_id, team_id):
        if season not in self.seasons:
            self.seasons[season] = ScheduleSeason(season)
        self.seasons[season].append_game(game_date, game_id, team_id)

    def get_matchups(self) -> List[ScheduleMatchup]:
        to_ret = []
        for season in self.seasons.values():
            to_ret.extend(season.get_mathcups())
        return to_ret


class LeagueSchedule(SharedDataResourceAbc[Schedule]):
    def __init__(self, season_type: SeasonType):
        self.season_type = season_type
        self.matchups: Optional[List[ScheduleMatchup]] = None
        self.last_season: int = -1
        super().__init__()

    def _fetch_data(self):
        to_ret = self.fetch_schedule()
        return to_ret

    @staticmethod
    def process_results(schedule: Schedule, results: List, headers: List):
        season_id_index = headers.index('SEASON_ID')
        team_id_index = headers.index('TEAM_ID')
        game_id_index = headers.index('GAME_ID')
        game_date_index = headers.index('GAME_DATE')
        for row in results:
            season = int(row[season_id_index][1:])
            team_id = row[team_id_index]
            game_id = row[game_id_index]
            game_date = NBA_GAME_IDS_GAME_DATE_CORRECTION[game_id] if game_id in NBA_GAME_IDS_GAME_DATE_CORRECTION else row[game_date_index]
            schedule.append_game(season, game_date, game_id, team_id)

    def fetch_schedule(self):
        start_date: Optional[datetime.date] = None
        continue_loop = True
        to_ret = Schedule()
        while continue_loop:
            to_send = BOXSCORES_ENDPOINT % (start_date.isoformat() if start_date else '', '', 'T',
                                            self.season_type.api_name)
            r = requests.get(to_send, headers=STATS_HEADERS)
            data = json.loads(r.content)
            if not data:
                break
            data = data["resultSets"][0]
            headers = data["headers"]
            results = data["rowSet"]
            game_date_index = headers.index("GAME_DATE")
            wl_index = headers.index('WL')
            if len(results) >= STATS_API_COUNT_THRESHOLD:
                last_date = results[-1][game_date_index]
                while results[-1][game_date_index] == last_date:
                    results.pop()
                start_date = datetime.date.fromisoformat(last_date)
            else:
                continue_loop = False
            # take only boxscores that occured in the past(5 days should be enough i guess) or finished(WL is not null)
            results = [r for r in results if r[wl_index] is not None or (
                    datetime.date.today() - datetime.date.fromisoformat(r[game_date_index])).days >= 5]
            self.process_results(to_ret, results, headers)
        return to_ret

    def get_matchups(self) -> List[ScheduleMatchup]:
        if self.matchups is None:
            schedule: Schedule = self.get_data()
            self.matchups = schedule.get_matchups()
        return self.matchups

    def get_last_season(self) -> int:
        if self.last_season == -1:
            self.last_season = max(self.matchups, key=lambda matchup: matchup.season).season
        return self.last_season


playoff_schedule = LeagueSchedule(PLAYOFFS_SEASON_TYPE)
