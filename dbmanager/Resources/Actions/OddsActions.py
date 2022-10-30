from abc import ABC
from typing import Union, List, Optional, Type
from sqlalchemy import delete, select, func, and_
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.Odds import Odds
from dbmanager.Downloaders.OddsDownloader import OddsDownloader
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.OddsActionSpecs import UpdateOdds, RedownloadOdds, \
    RedownloadOddsInSeasonsRange
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SharedData.BREFSeasonsLinks import bref_seasons_links
from dbmanager.SharedData.SeasonPlayoffs import get_last_season_with_playoffs, last_season_playoffs
from dbmanager.constants import FIRST_ODDS_SEASON, EXCLUDED_ODDS_SEASONS
from dbmanager.utils import iterate_with_next, retry_wrapper


class OddsGeneralAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session, start_season: Optional[int], end_season: Optional[int], update: bool):
        super().__init__(session)
        self.start_season: int = start_season if start_season else FIRST_ODDS_SEASON
        self.end_season: Optional[int] = end_season
        self.update: bool = update
        self.seasons_to_fetch: List[int] = []
        self.current_season: Optional[int] = None

    def init_task_data_abs(self) -> bool:
        self.end_season = self.end_season if self.end_season else get_last_season_with_playoffs()
        self.seasons_to_fetch: List[int] = self.get_seasons_to_fetch()
        self.current_season: Optional[int] = self.seasons_to_fetch[0] if self.seasons_to_fetch else None
        return len(self.seasons_to_fetch) > 0

    def get_seasons_to_fetch(self) -> List[int]:
        initial_list = [i for i in range(self.start_season, self.end_season + 1) if i not in EXCLUDED_ODDS_SEASONS]
        if not self.update:
            return initial_list
        to_ret = []
        last_rounds_stmt = (
            select(Odds.Season, func.min(Odds.Round)).
            where(and_(
                Odds.Season >= self.start_season,
                Odds.Season <= self.end_season
            )).
            group_by(Odds.Season)
        )
        last_rounds = self.session.execute(last_rounds_stmt).fetchall()
        last_rounds = {season: last_round for season, last_round in last_rounds}
        last_season = bref_seasons_links.max_nba_season()
        for season in initial_list:
            if (season not in last_rounds or
                    # dubious condition. this assumes that if you downloaded the data of old seasons once its enough
                    # so only new seasons may be partially downloaded
                    (last_season > season >= 2020 and last_rounds[season] > 1) or
                    (season == last_season and last_rounds[season] > last_season_playoffs.get_last_round())):
                to_ret.append(season)
        return to_ret

    def insert_odds(self, season: int, odds: List[dict]):
        delete_stmt = delete(Odds).where(Odds.Season == season)
        self.session.execute(delete_stmt)
        if odds:
            stmt = insert(Odds).on_conflict_do_nothing()
            self.session.execute(stmt, odds)
        self.session.commit()
        self.update_resource()

    @retry_wrapper
    async def collect_season_odds(self, season: int):
        downloader = OddsDownloader(season)
        odds_to_add = downloader.download()
        if odds_to_add is None:
            return
        self.insert_odds(season, odds_to_add)

    async def action(self):
        for season, next_season in iterate_with_next(self.seasons_to_fetch):
            await self.collect_season_odds(season)
            self.current_season = next_season
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.seasons_to_fetch)

    def get_current_subtask_text_abs(self) -> str:
        return gettext('resources.odds.actions.download_odds.downloading_odds_of_season',
                       season=self.current_season)


class UpdateOddsAction(OddsGeneralAction):

    def __init__(self, session: scoped_session):
        super().__init__(session, None, None, True)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdateOdds


class RedownloadOddsAction(OddsGeneralAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, None, None, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return RedownloadOdds


class RedownloadOddsInSeasonsRangeAction(OddsGeneralAction):
    def __init__(self, session: scoped_session, start_season: int, end_season: int):
        super().__init__(session, start_season, end_season, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return RedownloadOddsInSeasonsRange
