import datetime
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Union, Optional, List, Dict, Type
from sqlalchemy import select, and_, or_, bindparam, update, not_
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Downloaders.BREFStartersDownloader import BREFStartersDownloader
from dbmanager.Downloaders.NBAStartersDownloader import NBAStartersDownloader
from dbmanager.Logger import log_message
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.BREFStartersActionSpecs import get_starters_range, UpdateStarters, \
    RedownloadStarters, RedownloadStartersInSeasonsRange
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.DataTypes.SeasonType import PLAYIN_SEASON_TYPE
from dbmanager.SharedData.LiveMappings import live_mappings
from dbmanager.utils import iterate_with_next
from dbmanager.tasks.RetryManager import retry_wrapper


@dataclass
class MissingTeamSeason:
    season: int
    team_id: int
    team_name: str
    games_map: Dict[datetime.date, str]


@dataclass
class GameToUpdate:
    game_id: str
    team_id: int


@dataclass
class GameToUpdateWithStarter:
    game_id: str
    team_id: int
    player_id: int


@dataclass
class GameToFetch:
    game_id: str
    game_date: datetime.date
    matchup: str


class GeneralStartersAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session, start_season: Optional[int], end_season: Optional[int], to_update: bool):
        super().__init__(session)
        self.start_season: Optional[int] = start_season
        self.end_season: Optional[int] = end_season
        self.to_update: bool = to_update
        self.seasons_to_fetch: List[MissingTeamSeason] = []
        self.play_in_games_to_fetch: List[GameToFetch] = []
        self.current_season: Optional[MissingTeamSeason] = None
        self.current_game: Optional[GameToFetch] = None

    def init_task_data_abs(self) -> bool:
        min_season, max_season, count = get_starters_range(self.session)
        self.start_season = self.start_season if self.start_season else min_season
        self.end_season = self.end_season if self.end_season else max_season
        seasons_to_fetch, play_in_games_to_fetch = self.get_seasons_to_fetch()
        self.seasons_to_fetch = seasons_to_fetch
        self.play_in_games_to_fetch = play_in_games_to_fetch
        self.current_season = self.seasons_to_fetch[0] if self.seasons_to_fetch else None
        self.current_game = self.play_in_games_to_fetch[0] if self.play_in_games_to_fetch else None
        return len(self.play_in_games_to_fetch) + len(self.seasons_to_fetch) > 0

    def get_seasons_to_fetch(self):
        stmt = (
            select(BoxScoreP.Season, BoxScoreP.TeamId, BoxScoreP.TeamName,
                   BoxScoreP.Matchup, BoxScoreP.SeasonType,
                   BoxScoreP.GameId, BoxScoreP.GameDate)
            .where(and_(self.start_season <= BoxScoreP.Season,
                        self.end_season >= BoxScoreP.Season,
                        BoxScoreP.SeasonType.in_([2, 4, 5]),
                        or_(not_(self.to_update), BoxScoreP.Starter.is_(None))))
            .distinct()
        )
        available_seasons = self.session.execute(stmt).fetchall()
        # return all seasons with missing games
        grouped: dict[tuple[int, int, str], dict[datetime.date, str]] = defaultdict(dict)
        play_in_games_to_ret = []
        for season, team_id, team_name, matchup, season_type, game_id, game_date in available_seasons:
            if season_type == PLAYIN_SEASON_TYPE.code:
                if 'vs.' in matchup:
                    play_in_games_to_ret.append(GameToFetch(game_id, game_date, matchup))
            else:
                grouped[(season, team_id, team_name)][game_date] = game_id
        seasons_to_ret = [MissingTeamSeason(season, team_id, team_name, missing_games)
                          for (season, team_id, team_name), missing_games in grouped.items()]
        return seasons_to_ret, play_in_games_to_ret

    def update_boxscores_starters_all(self, games_to_update: List[GameToUpdate], games_with_starters: List[GameToUpdateWithStarter]):
        if not games_to_update or not games_with_starters:
            return
        update_starters_stmt = (
            update(BoxScoreP).
            where(and_(
                BoxScoreP.PlayerId == bindparam('player_id'),
                BoxScoreP.GameId == bindparam('game_id'),
                BoxScoreP.TeamId == bindparam('team_id'),
                BoxScoreP.Starter.is_(None)
            )).
            values(
                Starter=1
            )
        )
        update_bench_stmt = (
            update(BoxScoreP).
            where(and_(
                BoxScoreP.GameId == bindparam('game_id'),
                BoxScoreP.TeamId == bindparam('team_id'),
                BoxScoreP.Starter.is_(None)
            )).
            values(
                Starter=0
            )
        )
        starters_dicts = list(map(asdict, games_with_starters))
        games_dicts = list(map(asdict, games_to_update))
        self.session.execute(update_starters_stmt, starters_dicts)
        self.session.execute(update_bench_stmt, games_dicts)
        self.session.commit()
        self.update_resource()

    @retry_wrapper
    async def collect_team_season_starters(self, season: MissingTeamSeason):
        downloader = BREFStartersDownloader(season.season, season.team_id, live_mappings.get_data(self.session))
        games_with_starters = await downloader.download()
        starters_to_update = [
            GameToUpdateWithStarter(
                season.games_map[game_date],
                season.team_id,
                starter_id
            )
            for game_date, starters_ids in games_with_starters
            for starter_id in starters_ids
            if game_date in season.games_map]
        games_to_update = [
            GameToUpdate(
                season.games_map[game_date],
                season.team_id
            )
            for game_date, starters_ids in games_with_starters
            if game_date in season.games_map]
        self.update_boxscores_starters_all(games_to_update, starters_to_update)

    @retry_wrapper
    async def collect_game_starters(self, game: GameToFetch):
        downloader = NBAStartersDownloader(game.game_id)
        games_with_starters, games_rows_to_update = await downloader.download()
        starters_to_update = [
            GameToUpdateWithStarter(
                *game_with_starter
            )
            for game_with_starter in games_with_starters]
        games_to_update = [
            GameToUpdate(
                *game_to_update
            )
            for game_to_update in games_rows_to_update]
        self.update_boxscores_starters_all(games_to_update, starters_to_update)

    async def action(self):
        for team_season, next_team_season in iterate_with_next(self.seasons_to_fetch):
            await self.collect_team_season_starters(team_season)
            self.current_season = next_team_season
            await self.finish_subtask()
        for game_to_fetch, next_game_to_fetch in iterate_with_next(self.play_in_games_to_fetch):
            await self.collect_game_starters(game_to_fetch)
            self.current_game = next_game_to_fetch
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.seasons_to_fetch) + len(self.play_in_games_to_fetch)

    def get_current_subtask_text_abs(self) -> str:
        # fetching starters of {team_name} of season {season}
        # fetching starters of {matchup} ({game_date})
        if self.current_season:
            return gettext('resources.bref_starters.actions.download_starters.downloading_season_starters',
                           team=self.current_season.team_name,
                           season=self.current_season.season)
        return gettext('resources.bref_starters.actions.download_starters.downloading_game_starters',
                       matchup=self.current_game.matchup if self.current_game else '',
                       date=self.current_game.game_date.isoformat() if self.current_game else '')


class UpdateStartersAction(GeneralStartersAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, None, None, True)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdateStarters


class RedownloadStartersAction(GeneralStartersAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, None, None, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return RedownloadStarters


class RedownloadStartersInSeasonsRangeAction(GeneralStartersAction):
    def __init__(self, session: scoped_session, start_season: int, end_season: int):
        super().__init__(session, start_season, end_season, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return RedownloadStartersInSeasonsRange
