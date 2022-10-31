from abc import ABC
from typing import Union, Type, List, Optional
from sqlalchemy import select, func, delete
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFPlayoffSerie import BREFPlayoffSerie
from dbmanager.Downloaders.BREFPlayoffSeriesDownloader import BREFPlayoffSeriesDownloader
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.BREFPlayoffSeriesActionSpecs import UpdateBREFPlayoffSeries, \
    RedownloadBREFPlayoffSeries, RedownloadBREFPlayoffSeriesInSeasonsRange
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SharedData.BREFSeasonsLinks import BREFSeasonLink, bref_seasons_links
from dbmanager.utils import iterate_with_next
from dbmanager.tasks.RetryManager import retry_wrapper


class UpdateBREFPlayoffSeriesGeneralAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session, start_season: Optional[int], end_season: Optional[int], update: bool):
        super().__init__(session)
        self.start_season = start_season
        self.end_season = end_season
        self.update = update
        self.seasons_to_fetch_links: List[BREFSeasonLink] = []
        self.current_season_link: Optional[BREFSeasonLink] = None

    def init_task_data_abs(self) -> bool:
        if self.update:
            # TODO can be more efficient using the playoff schedule
            self.seasons_to_fetch_links = bref_seasons_links.get_nba_seasons_not_in_list(self.get_completed_series())
        else:
            self.seasons_to_fetch_links = bref_seasons_links.get_nba_seasons_in_range(self.start_season, self.end_season)
        self.current_season_link = self.seasons_to_fetch_links[0] if self.seasons_to_fetch_links else None
        return len(self.seasons_to_fetch_links) > 0

    def get_completed_series(self) -> List[int]:
        stmt = (
            select(BREFPlayoffSerie.Season).
            group_by(BREFPlayoffSerie.Season).
            having(func.min(BREFPlayoffSerie.SerieOrder).filter(BREFPlayoffSerie.IsOver == 1)
                   == 1)
        )
        res = self.session.execute(stmt).fetchall()
        return [r[0] for r in res]

    def insert_series_of_season(self, season_link: BREFSeasonLink, series):
        if not series:
            return
        delete_stmt = (
            delete(BREFPlayoffSerie).where(BREFPlayoffSerie.Season == season_link.season)
        )
        stmt = insert(BREFPlayoffSerie).on_conflict_do_nothing()
        self.session.execute(delete_stmt)
        self.session.execute(stmt, series)
        self.session.commit()
        self.update_resource()

    # updates series of a season
    @retry_wrapper
    async def update_playoff_summary(self, season_link: BREFSeasonLink):
        handler = BREFPlayoffSeriesDownloader(season_link)
        data = handler.download()
        if not data:
            return
        headers = [
            'Season',
            'TeamAId',
            'TeamAName',
            'TeamBId',
            'TeamBName',
            'TeamAWins',
            'TeamBWins',
            'WinnerId',
            'WinnerName',
            'LoserId',
            'LoserName',
            'SerieOrder',
            'LevelTitle',
            'SerieStartDate',
            'SerieEndDate',
            'IsOver'
        ]
        dicts = [dict(zip(headers, serie)) for serie in data]
        self.insert_series_of_season(season_link, dicts)

    async def action(self):
        for season_link, next_season_link in iterate_with_next(self.seasons_to_fetch_links):
            await self.update_playoff_summary(season_link)
            self.current_season_link = season_link
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.seasons_to_fetch_links)

    def get_current_subtask_text_abs(self) -> str:
        # fetching playoff series of season 1993
        return gettext('resources.bref_playoff_series.actions.update_bref_playoff_series.fetching_season_series',
                       season=self.seasons_to_fetch_links[self.completed_subtasks()].season if self.completed_subtasks() < len(self.seasons_to_fetch_links) else '')


class UpdateBREFPlayoffSeriesAction(UpdateBREFPlayoffSeriesGeneralAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, None, None, True)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdateBREFPlayoffSeries


class RedownloadBREFPlayoffSeriesAction(UpdateBREFPlayoffSeriesGeneralAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, None, None, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return RedownloadBREFPlayoffSeries


class RedownloadBREFPlayoffSeriesInSeasonsRangeAction(UpdateBREFPlayoffSeriesGeneralAction):
    def __init__(self, session: scoped_session, start_season: int, end_season: int):
        super().__init__(session, start_season, end_season, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return RedownloadBREFPlayoffSeriesInSeasonsRange
