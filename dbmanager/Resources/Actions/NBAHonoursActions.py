from abc import ABC, abstractmethod
from typing import Union, List, Optional, Type
from sqlalchemy import delete
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAHonours import NBAHonours
from dbmanager.Downloaders.TeamDetailsDownloader import TeamDetailsDownloader
from dbmanager.Logger import log_message
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import call_async_with_retry
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.NBAHonoursActionSpecs import DownloadAllHonours, DownloadTeamHonours
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SharedData.FranchisesHistory import franchises_history, FranchiseSpan
from dbmanager.utils import iterate_with_next


def transform_hof(team_id, row):
    return {
        'PlayerId': row[0] if row[0] else 0,
        'FullName': row[1],
        'Jersey': '#',
        'Position': '#',
        'TeamId': team_id,
        'Description': 'Hall of Fame Inductee',
        'Season': row[5] if row[5] else 0,
        'HonourType': 'HOF'
    }


def transform_retired_jersey(team_id, row):
    return {
        'PlayerId': row[0] if row[0] else 0,
        'FullName': row[1],
        'Jersey': row[3] if row[3] else '#',
        'Position': row[2] if row[2] else '#',
        'TeamId': team_id,
        'Description': 'Retired Jersey',
        'Season': row[5] if row[5] else 0,
        'HonourType': 'Retired Jersey'
    }


class GeneralDownloadHonoursAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session):
        super().__init__(session)
        self.teams_to_collect: List[FranchiseSpan] = []
        self.current_team: Optional[FranchiseSpan] = None

    def init_task_data_abs(self) -> bool:
        self.teams_to_collect = self.get_teams_to_collect()
        self.current_team = self.teams_to_collect[0] if self.teams_to_collect else None
        return len(self.teams_to_collect) > 0

    @abstractmethod
    def get_teams_to_collect(self) -> List[FranchiseSpan]:
        pass

    def insert_honours(self, team_id: int, honours: List[dict]):
        delete_stmt = delete(NBAHonours).where(NBAHonours.TeamId == team_id)
        self.session.execute(delete_stmt)
        if honours:
            stmt = insert(NBAHonours).on_conflict_do_nothing()
            self.session.execute(stmt, honours)
        self.session.commit()
        self.update_resource()

    async def collect_team_honours(self, team: FranchiseSpan):
        downloader = TeamDetailsDownloader(team.franchise_id)
        data = await call_async_with_retry(downloader.download)
        if not data:
            log_message(f'couldnt fetch honours of {team.franchise_name}({team.franchise_id}). try again later')
            return
        data = data['resultSets']
        hof_data = data[6]['rowSet']
        retired_data = data[7]['rowSet']
        honours = [transform_hof(team.franchise_id, r) for r in hof_data]
        honours.extend([transform_retired_jersey(team.franchise_id, r) for r in retired_data])
        self.insert_honours(team.franchise_id, honours)

    async def action(self):
        for team, next_team in iterate_with_next(self.teams_to_collect):
            await self.collect_team_honours(team)
            self.current_team = next_team
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.teams_to_collect)

    def get_current_subtask_text_abs(self) -> str:
        # fetching awards of {player_name}...
        return gettext('resources.nba_honours.actions.download_honours.fetching_honours_of_team',
                       team_id=self.current_team.franchise_id if self.current_team else '',
                       team_name=self.current_team.franchise_name if self.current_team else '')


class DownloadAllHonoursAction(GeneralDownloadHonoursAction):
    def __init__(self, session: scoped_session):
        super().__init__(session)

    def get_teams_to_collect(self) -> List[FranchiseSpan]:
        return franchises_history.get_franchises()

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadAllHonours


class DownloadTeamHonoursAction(GeneralDownloadHonoursAction):
    def __init__(self, session: scoped_session, team_id: int):
        super().__init__(session)
        self.team_id: int = team_id

    def get_teams_to_collect(self) -> List[FranchiseSpan]:
        return [franchises_history.get_last_span_with_id(self.team_id)]

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadTeamHonours
