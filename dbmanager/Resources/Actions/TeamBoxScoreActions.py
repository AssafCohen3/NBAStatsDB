import datetime
import re
from abc import ABC
from collections import defaultdict
from typing import Union, Optional, List, Any, Dict, Type
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreT import BoxScoreT
from dbmanager.Downloaders.BoxScoreDownloader import BoxScoreDownloader
from dbmanager.Logger import log_message
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import call_async_with_retry
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.TeamBoxScoreActionSpecs import UpdateTeamBoxScores, \
    ResetTeamBoxScores, UpdateTeamBoxScoresInDateRange
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SeasonType import get_season_types, SeasonType
from dbmanager.constants import STATS_API_COUNT_THRESHOLD, NBA_GAME_IDS_GAME_DATE_CORRECTION


def transform_boxscores(rows: List[Any], headers: List[str]) -> List[Dict[str, Any]]:
    renames = {
        'TEAM_ID': 'TeamId',
        'TEAM_ABBREVIATION': 'TeamAbbreviation',
        'TEAM_NAME': 'TeamName',
        'GAME_ID': 'GameId',
        'GAME_DATE': 'GameDate',
        'MATCHUP': 'Matchup',
        'PLUS_MINUS': 'PlusMinus',
        'FANTASY_PTS': 'FantasyPts',
        'VIDEO_AVAILABLE': 'VideoAvailable'
    }

    def get_row_dict(row):
        to_ret: Dict = dict(zip(headers, row))
        to_ret['IsHome'] = 0 if '@' in to_ret['Matchup'] else 1
        season_id = to_ret['SEASON_ID']
        season_and_type = re.findall(r'(\d)(\d*)', season_id)[0]
        to_ret["SeasonType"] = season_and_type[0]
        to_ret["Season"] = int(season_and_type[1])
        game_date = NBA_GAME_IDS_GAME_DATE_CORRECTION[to_ret['GameId']] if to_ret['GameId'] in NBA_GAME_IDS_GAME_DATE_CORRECTION else to_ret['GameDate']
        to_ret['GameDate'] = datetime.date.fromisoformat(game_date)
        to_ret.pop('SEASON_ID')
        return to_ret

    headers = [renames[h] if h in renames else h for h in headers]
    initial_dicts = [get_row_dict(row) for row in rows]
    games_dict = defaultdict(lambda: defaultdict(list))
    for d in initial_dicts:
        games_dict[d['GameId']][d['TeamId']].append(d)
    for game_id, teams_dict in games_dict.items():
        team_a_id, team_b_id = sorted(teams_dict.keys())
        team_a_name, team_b_name = teams_dict[team_a_id][0]['TeamName'], teams_dict[team_b_id][0]['TeamName']
        for t in teams_dict.values():
            for p in t:
                p['TeamAId'] = team_a_id
                p['TeamAName'] = team_a_name
                p['TeamBId'] = team_b_id
                p['TeamBName'] = team_b_name
    return initial_dicts


# returns the last saved date of some box score type plus 1 day(empty string if none found)
def get_last_game_date(session: scoped_session, season_type: SeasonType) -> Optional[datetime.date]:
    stmt = select(BoxScoreT.GameDate).where(BoxScoreT.SeasonType == season_type.code).order_by(
        BoxScoreT.GameDate.desc()).limit(1)
    res = session.execute(stmt).fetchall()
    return res[0][0] if res else None


class GeneralResetTeamBoxScoresAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session,
                 season_type_code: str,
                 start_date: datetime.date = None,
                 end_date: datetime.date = None,
                 replace: bool = False,
                 update: bool = False):
        super().__init__(session)
        self.last_fetched_date: Optional[datetime.date] = start_date
        self.start_date: Optional[datetime.date] = start_date
        self.end_date: Optional[datetime.date] = end_date
        self.season_types: List[SeasonType] = get_season_types(season_type_code)
        self.current_season_type_index = 0
        self.replace = replace
        self.update = update

    def insert_boxscores(self, session: scoped_session, boxscores: List[Dict[str, Any]], replace: bool):
        if not boxscores:
            return
        stmt = insert(BoxScoreT)
        if replace:
            stmt = stmt.on_conflict_do_update(set_={
                c.name: c for c in stmt.excluded
            })
        else:
            stmt = stmt.on_conflict_do_nothing()
        session.execute(stmt, boxscores)
        session.commit()
        self.update_resource()

    async def fetch_season_type_boxscores(self, season_type: SeasonType):
        continue_loop = True
        while continue_loop:
            downloader = BoxScoreDownloader(
                self.last_fetched_date,
                self.end_date,
                season_type, 'T'
            )
            data = await call_async_with_retry(downloader.download)
            if not data:
                break
            data = data["resultSets"][0]
            headers = data["headers"]
            results = data["rowSet"]
            log_message(
                f"found {len(results)} teams boxscores in {season_type.name} from date {self.last_fetched_date}")
            game_date_index = headers.index("GAME_DATE")
            wl_index = headers.index('WL')
            if len(results) >= STATS_API_COUNT_THRESHOLD:
                last_date = results[-1][game_date_index]
                while results[-1][game_date_index] == last_date:
                    results.pop()
                self.last_fetched_date = datetime.date.fromisoformat(last_date)
            else:
                continue_loop = False
            # take only boxscores that occured in the past(5 days should be enough i guess) or finished(WL is not null)
            results = [r for r in results if r[wl_index] is not None or (
                    datetime.date.today() - datetime.date.fromisoformat(r[game_date_index])).days >= 5]
            transformed = transform_boxscores(results, headers)
            self.insert_boxscores(self.session, transformed, self.replace)
            await self.finish_subtask()

    async def action(self):
        for i, season_type in enumerate(self.season_types):
            if self.update:
                self.start_date = get_last_game_date(self.session, season_type)
            self.last_fetched_date = self.start_date
            self.current_season_type_index = i
            await self.fetch_season_type_boxscores(season_type)

    def subtasks_count(self) -> Union[int, None]:
        return None

    def get_current_subtask_text_abs(self) -> str:
        # fetching boxscores of type Regular Season between 1976-01-01 and 1976-01-02
        if self.end_date is None:
            return gettext('resources.teamboxscore.actions.update_team_boxscores.fetching_boxscores_of_type_since_date',
                           season_type=self.season_types[self.current_season_type_index].name,
                           start_date=self.last_fetched_date.isoformat() if self.last_fetched_date else '')
        else:
            return gettext('resources.teamboxscore.actions.update_team_boxscores.fetching_boxscores_of_type_in_date_range',
                           season_type=self.season_types[self.current_season_type_index].name,
                           start_date=self.last_fetched_date.isoformat() if self.last_fetched_date else '',
                           end_date=self.end_date.isoformat())


class UpdateTeamBoxScoresAction(GeneralResetTeamBoxScoresAction):
    def __init__(self, session: scoped_session,
                 season_type_code: str):
        super().__init__(session, season_type_code, None, None, False, True)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdateTeamBoxScores


class ResetTeamBoxScoresAction(GeneralResetTeamBoxScoresAction):
    def __init__(self, session: scoped_session,
                 season_type_code: str):
        super().__init__(session, season_type_code, None, None, True, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return ResetTeamBoxScores


class UpdateTeamBoxScoresInDateRangeAction(GeneralResetTeamBoxScoresAction):
    def __init__(self, session: scoped_session,
                 season_type_code: str,
                 start_date: datetime.date = None, end_date: datetime.date = None):
        super().__init__(session, season_type_code, start_date, end_date, True, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdateTeamBoxScoresInDateRange