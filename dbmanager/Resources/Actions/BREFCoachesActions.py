import re
from abc import ABC
from collections import defaultdict
from typing import Optional, List, Union, Type, Dict

from bs4 import BeautifulSoup
from sqlalchemy import delete, insert
from sqlalchemy.orm import scoped_session
from unidecode import unidecode

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFCoachSeason import BREFCoachSeason
from dbmanager.Downloaders.BREFCoachesDownloader import BREFCoachesDownloader
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.BREFCoachesActionSpecs import DownloadAllCoaches, \
    DownloadCoachesInSeasonsRange
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SharedData.BREFSeasonsLinks import BREFSeasonLink, bref_seasons_links
from dbmanager.constants import BREF_ABBREVATION_TO_NBA_TEAM_ID, TEAM_NBA_ID_TO_NBA_NAME
from dbmanager.utils import iterate_with_next
from dbmanager.tasks.RetryManager import retry_wrapper


def get_team_id_by_bref_abbr(abbr: str, season: int):
    return [a for a in BREF_ABBREVATION_TO_NBA_TEAM_ID[abbr] if a[0] <= season <= a[1]][0][2]


class GeneralDownloadCoachesAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session, start_season: Optional[int], end_season: Optional[int]):
        super().__init__(session)
        self.start_season = start_season
        self.end_season = end_season
        self.seasons_to_collect: List[BREFSeasonLink] = []
        self.current_season: Optional[BREFSeasonLink] = None

    def init_task_data_abs(self) -> bool:
        self.seasons_to_collect = bref_seasons_links.get_nba_seasons_in_range(self.start_season, self.end_season)
        self.current_season = self.seasons_to_collect[0] if self.seasons_to_collect else None
        return len(self.seasons_to_collect) > 0

    def insert_coaches(self, season: int, coaches: List[dict]):
        delete_stmt = delete(BREFCoachSeason).where(BREFCoachSeason.Season == season)
        self.session.execute(delete_stmt)
        if coaches:
            stmt = insert(BREFCoachSeason)
            self.session.execute(stmt, coaches)
        self.session.commit()
        self.update_resource()

    @retry_wrapper
    async def collect_season_coaches(self, season_link: BREFSeasonLink):
        downloader = BREFCoachesDownloader(season_link.leagu_id, season_link.season)
        resp = downloader.download()
        soup = BeautifulSoup(resp, 'html.parser')
        coaches_rows = soup.select(f'#{season_link.leagu_id}_coaches tbody tr')
        # to contain the coaches we found for now
        teams_coaches: Dict[int, List[Dict]] = defaultdict(list)
        for row in coaches_rows:
            if row.has_attr('class'):
                continue
            coach_link = row.select(f'[data-stat="coach"]')[0].select('a')[0]
            coach_id = re.findall(r'/([a-z0-9]+)\.html$', coach_link['href'])[0]
            coach_name = unidecode(coach_link.get_text())
            team_tag = row.select('[data-stat="team"]')[0]
            team_abbr = team_tag.select('a')
            team_abbr = team_abbr[0].get_text() if team_abbr else team_tag.get_text()
            team_id = get_team_id_by_bref_abbr(team_abbr, season_link.season)
            team_name = TEAM_NBA_ID_TO_NBA_NAME[team_id]
            games_num = int(row.select('[data-stat="cur_g"]')[0].get_text())
            new_coach_season = {
                'Season': season_link.season,
                'CoachId': coach_id,
                'CoachName': coach_name,
                'TeamId': team_id,
                'TeamName': team_name,
                'FromGameNumber': 1,
                'ToGameNumber': None,
                'RegularSeasonGamesCount': games_num
            }
            if teams_coaches[team_id]:
                last_coach['ToGameNumber'] = (last_coach := teams_coaches[team_id][-1])['FromGameNumber'] + last_coach['RegularSeasonGamesCount']
                new_coach_season['FromGameNumber'] = last_coach['ToGameNumber'] + 1
            teams_coaches[team_id].append(new_coach_season)
        to_insert = [coach for team_id, coaches in teams_coaches.items() for coach in coaches]
        self.insert_coaches(season_link.season, to_insert)

    async def action(self):
        for season, next_season in iterate_with_next(self.seasons_to_collect):
            await self.collect_season_coaches(season)
            self.current_season = next_season
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.seasons_to_collect)

    def get_current_subtask_text_abs(self) -> str:
        # downloading {season} coaches
        return gettext('resources.bref_coaches.actions.download_coaches.downloading_coaches',
                       season=self.current_season.season if self.current_season else '')


class DownloadAllCoachesAction(GeneralDownloadCoachesAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, None, None)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadAllCoaches


class DownloadCoachesInSeasonsRangeAction(GeneralDownloadCoachesAction):
    def __init__(self, session: scoped_session, start_season: int, end_season: int):
        super().__init__(session, start_season, end_season)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadCoachesInSeasonsRange
