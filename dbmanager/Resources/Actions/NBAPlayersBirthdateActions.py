import datetime
import heapq
from abc import ABC
from dataclasses import dataclass, field
from typing import Union, List, Optional, Type, Tuple, Set
from sqlalchemy import select, func, and_, update, bindparam
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Database.Models.NBAPlayer import NBAPlayer
from dbmanager.Downloaders.PlayerProfileDownloader import PlayerProfileDownloader
from dbmanager.Downloaders.TeamRosterDownloader import TeamRosterDownloader
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import call_async_with_retry
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.NBAPlayersBirthdateActionSpecs import UpdatePlayersBirthdate, DownloadPlayersBirthdateInSeasonRange, RedownloadPlayersBirthdate
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SeasonType import REGULAR_SEASON_TYPE
from dbmanager.utils import iterate_with_next


@dataclass(unsafe_hash=True)
class PlayerToCollect:
    player_id: int
    player_name: str = field(compare=False)


@dataclass(unsafe_hash=True, order=True)
class TeamSeason:
    season: int
    team_id: int
    team_name: str = field(compare=False)
    expected_players: Set[PlayerToCollect] = field(compare=False)


@dataclass(order=True)
class CoverResult:
    score: int
    team_season: TeamSeason


def greedy_set_cover(subsets: List[TeamSeason], parent_set: Set[PlayerToCollect]) -> List[TeamSeason]:
    parent_set = set(parent_set)
    max_set_len = len(parent_set)
    heap: List[CoverResult] = []
    for team_season in subsets:
        # the score is max - roster size. since this is a min heap the heap head will be the roster with the maximum size
        heapq.heappush(heap, CoverResult(max_set_len - len(team_season.expected_players), team_season))
    results: List[TeamSeason] = []
    result_set = set()
    while result_set < parent_set:
        best: Optional[CoverResult] = None
        unused: List[CoverResult] = []
        while heap:
            cover_result = heapq.heappop(heap)
            if not best:
                best = CoverResult(max_set_len - len(cover_result.team_season.expected_players - result_set), cover_result.team_season)
                continue
            if cover_result.score >= best.score:
                heapq.heappush(heap, cover_result)
                break
            cover_result.score = max_set_len - len(cover_result.team_season.expected_players - result_set)
            if cover_result.score >= best.score:
                unused.append(cover_result)
            else:
                unused.append(best)
                best = cover_result
        results.append(best.team_season)
        result_set.update(best.team_season.expected_players)
        while unused:
            heapq.heappush(heap, unused.pop())
    return sorted(results, key=lambda r: (r.season, r.team_id))


class GeneralDownloadPlayersBirthdateAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session, start_season: Optional[int], end_season: Optional[int], to_update: bool):
        super().__init__(session)
        self.start_season = start_season
        self.end_season = end_season
        self.to_update = to_update
        self.team_seasons_to_collect: List[TeamSeason] = []
        self.current_team_season: Optional[TeamSeason] = None
        self.expected_players: Set[PlayerToCollect] = set()
        self.players_profiles_to_collect: List[PlayerToCollect] = []
        self.current_player_profile: Optional[PlayerToCollect] = None

    def init_task_data_abs(self) -> bool:
        team_seasons_to_collect, expected_players = self.get_resources_to_collect()
        self.team_seasons_to_collect = team_seasons_to_collect
        self.current_team_season = self.team_seasons_to_collect[0] if len(self.team_seasons_to_collect) > 0 else None
        self.expected_players = expected_players
        return len(self.expected_players) > 0

    def get_resources_to_collect(self) -> Tuple[List[TeamSeason], Set[PlayerToCollect]]:
        expected_players = set()
        cover_players = set()
        stmt = (
            select(NBAPlayer.PlayerId, NBAPlayer.FirstName + ' ' + NBAPlayer.LastName,
                   BoxScoreP.TeamId, BoxScoreP.TeamName, BoxScoreP.Season, func.max(BoxScoreP.GameDate))
            .outerjoin(BoxScoreP, and_(BoxScoreP.PlayerId == NBAPlayer.PlayerId, BoxScoreP.SeasonType == REGULAR_SEASON_TYPE.code))
        )
        if self.start_season:
            stmt = stmt.where(NBAPlayer.FirstSeason >= self.start_season)
        if self.end_season:
            stmt = stmt.where(NBAPlayer.FirstSeason <= self.end_season)
        if self.to_update:
            stmt = stmt.where(NBAPlayer.BirthDate.is_(None))
        stmt = stmt.group_by(BoxScoreP.Season, NBAPlayer.PlayerId)
        res = self.session.execute(stmt).fetchall()
        teams_rosters = {}
        for player_id, player_name, team_id, team_name, season, _ in res:
            player_to_add = PlayerToCollect(player_id, player_name)
            expected_players.add(player_to_add)
            if season:
                if (season, team_id) not in teams_rosters:
                    teams_rosters[(season, team_id)] = TeamSeason(season, team_id, team_name, set())
                teams_rosters[(season, team_id)].expected_players.add(player_to_add)
                cover_players.add(player_to_add)
        res = greedy_set_cover(list(teams_rosters.values()), cover_players)
        return res, expected_players

    def insert_players_birthdate(self, players_birthdates):
        if not players_birthdates:
            return
        stmt = (
            update(NBAPlayer).
            where(NBAPlayer.PlayerId == bindparam('PlayerIdToUpdate')).
            values(
                BirthDate=bindparam('NewBirthDate')
            )
        )
        self.session.execute(stmt, players_birthdates)
        self.session.commit()
        self.update_resource()

    async def collect_team_roster(self, team_season: TeamSeason):
        downloader = TeamRosterDownloader(team_season.season, team_season.team_id)
        data = await call_async_with_retry(downloader.download)
        data = data['resultSets'][0]['rowSet']
        players = [
            {
                'NewBirthDate': datetime.datetime.strptime(p[10], '%b %d, %Y').date(),
                'PlayerIdToUpdate': p[14]
            } for p in data
        ]
        to_remove = [PlayerToCollect(p[14], '') for p in data]
        self.expected_players.difference_update(to_remove)
        self.insert_players_birthdate(players)

    async def fetch_player_profile(self, player: PlayerToCollect):
        downloader = PlayerProfileDownloader(player.player_id)
        data = await call_async_with_retry(downloader.download)
        data = data['resultSets'][0]['rowSet']
        players = [
            {
                'NewBirthDate': datetime.datetime.fromisoformat(data[0][7]).date(),
                'PlayerIdToUpdate': data[0][0]
            }
        ]
        to_remove = [PlayerToCollect(p[0], '') for p in data]
        self.expected_players.difference_update(to_remove)
        self.insert_players_birthdate(players)

    async def action(self):
        for team_season, next_team_season in iterate_with_next(self.team_seasons_to_collect):
            await self.collect_team_roster(team_season)
            self.current_team_season = next_team_season
            await self.finish_subtask()
        self.players_profiles_to_collect = list(self.expected_players)
        self.current_player_profile = self.players_profiles_to_collect[0] if self.players_profiles_to_collect else None
        for player, next_player in iterate_with_next(self.players_profiles_to_collect):
            await self.fetch_player_profile(player)
            self.current_player_profile = next_player
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.team_seasons_to_collect) + len(self.players_profiles_to_collect)

    def get_current_subtask_text_abs(self) -> str:
        # fetching birthdates of the {team_name} ({season}) roster
        # fetching birthdate of {player_name}
        if self.current_team_season:
            return gettext('resources.nba_players_birthdate.actions.download_birthdates.downloading_team_roster_birthdates',
                           team=self.current_team_season.team_name,
                           season=self.current_team_season.season)
        return gettext('resources.nba_players_birthdate.actions.download_birthdates.downloading_player_birthdate',
                       player=self.current_player_profile.player_name if self.current_player_profile else '')


class UpdatePlayersBirthdateAction(GeneralDownloadPlayersBirthdateAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, None, None, True)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdatePlayersBirthdate


class RedownloadPlayersBirthdateAction(GeneralDownloadPlayersBirthdateAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, None, None, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return RedownloadPlayersBirthdate


class DownloadPlayersBirthdateInSeasonsRangeAction(GeneralDownloadPlayersBirthdateAction):
    def __init__(self, session: scoped_session, start_season: int, end_season: int):
        super().__init__(session, start_season, end_season, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadPlayersBirthdateInSeasonRange
