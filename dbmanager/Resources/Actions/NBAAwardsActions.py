import datetime
from abc import ABC, abstractmethod
from typing import Union, List, Optional, Type

import unidecode
from sqlalchemy import delete
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAAwards import NBAAwards
from dbmanager.Downloaders.NBAAwardsDownloader import NBAAwardsDownloader
from dbmanager.Logger import log_message
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import call_async_with_retry
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.NBAAwardsActionSpecs import DownloadAllPlayersAwards, \
    DownloadActivePlayersAwards, DownloadRookiesAwardsInSeasonsRange, DownloadPlayerAwards
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SharedData.FranchisesHistory import franchises_history, FranchiseSpan
from dbmanager.SharedData.PlayersIndex import PlayerDetails, players_index
from dbmanager.utils import iterate_with_next


def transform_award(award_row):
    full_name = award_row[1] + ' ' + award_row[2]
    season = int(award_row[6].split('-')[0]) if award_row[6] else 0
    candidate_teams: List[FranchiseSpan] = franchises_history.get_spans_in_range(award_row[3], season)
    if len(candidate_teams) == 0:
        team_id = award_row[3] if award_row[3] else 0
    else:
        team_id = candidate_teams[0].franchise_id
    date_awarded = datetime.datetime.strptime(award_row[7], '%m/%d/%Y').date() if award_row[7] else (
        datetime.datetime.fromisoformat(award_row[8]).date() if award_row[8] else datetime.datetime.min.date())

    to_ret = {
        'PlayerId': award_row[0],
        'FullName': unidecode.unidecode(full_name).strip(),
        'TeamId': team_id,
        'TeamName': award_row[3],
        'Description': award_row[4] if award_row[4] else '',
        'AllNBATeamNumber': int(award_row[5]) if award_row[5] and award_row[5] != '(null)' else None,
        'Season': season,
        'DateAwarded': date_awarded,
        'Confrence': award_row[9],
        'AwardType': award_row[10],
        'SubTypeA': award_row[11],
        'SubTypeB': award_row[12],
        'SubTypeC': award_row[13]
    }
    return to_ret


class GeneralDownloadAwardsAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session):
        super().__init__(session)
        self.players_to_collect: List[PlayerDetails] = []
        self.current_player: Optional[PlayerDetails] = None

    def init_task_data_abs(self) -> bool:
        self.players_to_collect = self.get_players_to_collect()
        self.current_player: Optional[PlayerDetails] = self.players_to_collect[0] if len(self.players_to_collect) > 0 else None
        return len(self.players_to_collect) > 0

    @abstractmethod
    def get_players_to_collect(self) -> List[PlayerDetails]:
        pass

    def insert_awards(self, player_id: int, awards: List[dict]):
        delete_stmt = delete(NBAAwards).where(NBAAwards.PlayerId == player_id)
        self.session.execute(delete_stmt)
        if awards:
            stmt = insert(NBAAwards).on_conflict_do_nothing()
            self.session.execute(stmt, awards)
        self.session.commit()
        self.update_resource()

    async def collect_player_awards(self, player: PlayerDetails):
        downloader = NBAAwardsDownloader(player.player_id)
        data = await call_async_with_retry(downloader.download)
        if not data:
            log_message(f'couldnt fetch awards of {player.player_name}({player.player_id}). try again later')
            return
        data = data['resultSets'][0]['rowSet']
        awards = [transform_award(p) for p in data]
        self.insert_awards(player.player_id, awards)

    async def action(self):
        for player, next_player in iterate_with_next(self.players_to_collect):
            await self.collect_player_awards(player)
            self.current_player = player
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.players_to_collect)

    def get_current_subtask_text_abs(self) -> str:
        # fetching awards of {player_name}...
        return gettext('resources.nba_awards.actions.download_awards.fetching_awards_of_player',
                       player_id=self.current_player.player_id if self.current_player else '',
                       player_name=self.current_player.player_name if self.current_player else '')


class DownloadAllPlayersAwardsAction(GeneralDownloadAwardsAction):
    def __init__(self, session: scoped_session):
        super().__init__(session)

    def get_players_to_collect(self) -> List[PlayerDetails]:
        return players_index.get_players()

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadAllPlayersAwards


class DownloadActivePlayersAwardsAction(GeneralDownloadAwardsAction):
    def __init__(self, session: scoped_session):
        super().__init__(session)

    def get_players_to_collect(self) -> List[PlayerDetails]:
        return [p for p in players_index.get_players() if p.active]

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadActivePlayersAwards


class DownloadRookiesAwardsInSeasonsRangeAction(GeneralDownloadAwardsAction):
    def __init__(self, session: scoped_session, start_season: int, end_season: int):
        super().__init__(session)
        self.start_season: int = start_season
        self.end_season: int = end_season

    def get_players_to_collect(self) -> List[PlayerDetails]:
        return [p for p in players_index.get_players() if self.start_season <= p.first_season <= self.end_season]

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadRookiesAwardsInSeasonsRange


class DownloadPlayerAwardsAction(GeneralDownloadAwardsAction):
    def __init__(self, session: scoped_session, player_id: int):
        super().__init__(session)
        self.player_id: int = player_id

    def get_players_to_collect(self) -> List[PlayerDetails]:
        return [players_index.get_player_details(self.player_id)]

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadPlayerAwards
