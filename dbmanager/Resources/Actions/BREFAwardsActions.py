import datetime
import logging
import re
from abc import ABC, abstractmethod
from typing import Optional, List, Union, Type, Dict

from bs4 import BeautifulSoup
from sqlalchemy import delete, insert
from sqlalchemy.orm import scoped_session
from unidecode import unidecode

from dbmanager.AppI18n import gettext
from dbmanager.DataTypes.BREFAwardConst import BREFAwardToFetch, AwardTypes, AWARDS, get_awards
from dbmanager.Database.Models.BREFAwards import BREFAwards
from dbmanager.Downloaders.BREFAwardDownloader import BREFAwardDownloader
from dbmanager.Downloaders.BREFPlayerPageDownloader import BREFPlayerPageDownloader
from dbmanager.Errors import ActionFailedError
from dbmanager.Logger import log_message
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.BREFAwardsActionSpecs import DownloadAllAwards, DownloadSpecificAward
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.constants import BREF_ABBREVATION_TO_NBA_TEAM_ID, TEAM_NBA_ID_TO_NBA_NAME
from dbmanager.utils import iterate_with_next
from dbmanager.tasks.RetryManager import retry_wrapper


def get_team_id_by_bref_abbr(abbr: str, season: int):
    return [a for a in BREF_ABBREVATION_TO_NBA_TEAM_ID[abbr] if a[0] <= season <= a[1]][0][2]


async def get_player_last_team_in_season(player_id: str, season: int):
    downloader = BREFPlayerPageDownloader(player_id)
    resp = await downloader.download()
    soup = BeautifulSoup(resp, 'html.parser')
    last_team_in_season = soup.select(rf'#per_game tbody tr#per_game\.{season + 1}')[-1]
    team_tag = last_team_in_season.select('[data-stat="team_id"]')[0]
    team_id = get_team_id_by_bref_abbr(team_tag.select('a')[0].get_text(), season)
    return team_id


async def fetch_season_award(award: BREFAwardToFetch, award_page_html: str):
    soup = BeautifulSoup(award_page_html, 'html.parser')
    to_ret = []
    awards_rows = soup.select(f'#{award.award_id}_NBA tbody tr, #{award.award_id}NBA tbody tr', {'class': ''})
    for row in awards_rows:
        season_tag = row.select('[data-stat="season"]')[0]
        season = int(season_tag.select('a')[0].get_text().split('-')[0])
        player_link = row.select(f'[data-stat="{award.person_type}"]')[0].select('a')[0]
        player_id = re.findall(r'/([a-z0-9]+)\.html$', player_link['href'])[0]
        player_name = unidecode(player_link.get_text())
        team_tag = row.select('[data-stat="team_id"]')[0]
        team_abbr = team_tag.select('a')
        team_abbr = team_abbr[0].get_text() if team_abbr else team_tag.get_text()
        team_id = (
            get_team_id_by_bref_abbr(team_abbr, season)
            if team_abbr != 'TOT' else
            await get_player_last_team_in_season(player_id, season)
        )
        team_name = TEAM_NBA_ID_TO_NBA_NAME[team_id]
        to_ret.append({
            'PersonId': player_id,
            'PersonName': player_name,
            'TeamId': team_id,
            'TeamName': team_name,
            'Season': season,
            'AwardId': award.award_id,
            'AwardName': award.award_name,
        })
    return to_ret


def fetch_season_all_nba_team_award(award: BREFAwardToFetch, award_page_html: str):
    soup = BeautifulSoup(award_page_html, 'html.parser')
    to_ret = []
    all_nba_teams_rows = soup.select(f'#awards_{award.award_id} tbody tr')
    for row in all_nba_teams_rows:
        if row.has_attr('class'):
            continue
        season_tag = row.select('[data-stat="season"]')[0]
        season = int(season_tag.select('a')[0].get_text().split('-')[0])
        league_id = row.select('[data-stat="lg_id"] a')[0].get_text()
        if league_id not in ('NBA', 'BAA'):
            continue
        team_number = int(row.select('[data-stat="all_team"]')[0].get_text()[0])
        for i in range((offset := (team_number - 1) * 5 + 1), offset + 6):
            player_tag = row.select(f'[data-stat="{i}"]')
            if not player_tag:
                continue
            player_tag = player_tag[0]
            links = player_tag.select('a')
            if links:
                player_link = links[0]
                player_id = re.findall(r'/([a-z0-9]+)\.html$', player_link['href'])[0]
                player_name = unidecode(player_link.get_text())
                res = {
                    'PersonId': player_id,
                    'PersonName': player_name,
                    'Season': season,
                    'AwardId': award.award_id,
                    'AwardName': award.award_name,
                    'AllNBATeamNumber': team_number,
                }
                to_ret.append(res)
    return to_ret


def fetch_honorary_awards(award: BREFAwardToFetch, award_page_html: str):
    soup = BeautifulSoup(award_page_html, 'html.parser')
    to_ret = []
    awards_rows = soup.select(f'#stats tbody tr', {'class': ''})
    for row in awards_rows:
        if row.has_attr('class'):
            continue
        player_link = row.select(f'[data-stat="{award.person_type}"]')[0].select('a')[0]
        player_id = re.findall(r'/([a-z0-9]+)\.html$', player_link['href'])[0]
        player_name = unidecode(player_link.get_text())
        to_ret.append({
            'PersonId': player_id,
            'PersonName': player_name,
            'AwardId': award.award_id,
            'AwardName': award.award_name,
        })
    return to_ret


def fetch_month_awards(award: BREFAwardToFetch, award_page_html: str):
    soup = BeautifulSoup(award_page_html, 'html.parser')
    to_ret = []
    seasons_grids = soup.select(f'.data_grid_group')
    for season_grid in seasons_grids:
        season = int(season_grid.select('h3')[0].get_text().split('-')[0])
        months_grids = season_grid.select('.data_grid_box')
        for month_grid in months_grids:
            month_name = month_grid.select('.gridtitle')[0].get_text()
            month_number = datetime.datetime.strptime(month_name, '%B').month
            year = season if month_number >= 10 else season + 1
            paragraphs = month_grid.select(f'p div p')
            for paragraph in paragraphs:
                week_title = paragraph.select('strong')
                if week_title:
                    date_str = f'{year} {week_title[0].get_text()}'
                    award_date = datetime.datetime.strptime(date_str, '%Y %b %d').date()
                else:
                    award_date = datetime.date(year, month_number, 1)
                players_links = paragraph.select('a')
                for player_link in players_links:
                    player_id = re.findall(r'/([a-z0-9]+)\.html$', player_link['href'])[0]
                    player_name = unidecode(player_link.get_text())
                    to_ret.append({
                        'PersonId': player_id,
                        'PersonName': player_name,
                        'AwardId': award.award_id,
                        'AwardName': award.award_name,
                        'Season': season,
                        'Conference': (
                            'East' if 'Eastern' in player_link['data-desc']
                            else 'West' if 'Western' in player_link['data-desc']
                            else None
                        ),
                        'DateAwarded': award_date,
                    })
    return to_ret


class GeneralDownloadAwardsAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session):
        super().__init__(session)
        self.awards_to_collect: List[BREFAwardToFetch] = []
        self.current_award: Optional[BREFAwardToFetch] = None

    def init_task_data_abs(self) -> bool:
        self.awards_to_collect = self.get_awards_to_collect()
        self.current_award = self.awards_to_collect[0] if self.awards_to_collect else None
        return len(self.awards_to_collect) > 0

    @abstractmethod
    def get_awards_to_collect(self) -> List[BREFAwardToFetch]:
        pass

    def insert_awards(self, award_id: str, awards: List[Dict]):
        log_message(f'inserting {len(awards)} bref awards of type {award_id}')
        delete_stmt = delete(BREFAwards).where(BREFAwards.AwardId == award_id)
        self.session.execute(delete_stmt)
        if awards:
            stmt = insert(BREFAwards)
            self.session.execute(stmt, awards)
        self.session.commit()
        self.update_resource()

    @retry_wrapper
    async def collect_award(self, award: BREFAwardToFetch):
        downloader = BREFAwardDownloader(award.award_id)
        award_html = await downloader.download()
        if award.award_type == AwardTypes.SEASON_PLAYER:
            to_insert = await fetch_season_award(award, award_html)
        elif award.award_type == AwardTypes.SEASON_ALL_NBA_TEAM:
            to_insert = fetch_season_all_nba_team_award(award, award_html)
        elif award.award_type == AwardTypes.MONTHLY:
            to_insert = fetch_month_awards(award, award_html)
        elif award.award_type == AwardTypes.HONORARY:
            to_insert = fetch_honorary_awards(award, award_html)
        else:
            raise ActionFailedError(self.get_action_spec(), f'{award.award_type.name} is ilegal')
        base_dict = {
            'DateAwarded': datetime.datetime.min.date(),
            'Season': 0,
            'PersonType': award.person_type,
        }
        to_insert = [{**base_dict, **award_to_insert} for award_to_insert in to_insert]
        self.insert_awards(award.award_id, to_insert)

    async def action(self):
        for award, next_award in iterate_with_next(self.awards_to_collect):
            await self.collect_award(award)
            self.current_award = next_award
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.awards_to_collect)

    def get_current_subtask_text_abs(self) -> str:
        # downloading {award} titles
        return gettext('resources.bref_awards.actions.download_awards.downloading_award',
                       award=self.current_award.award_name if self.current_award else '')


class DownloadAllAwardsAction(GeneralDownloadAwardsAction):

    def get_awards_to_collect(self) -> List[BREFAwardToFetch]:
        return AWARDS

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadAllAwards


class DownloadSpecificAwardAction(GeneralDownloadAwardsAction):
    def __init__(self, session: scoped_session, award_id: str):
        super().__init__(session)
        self.award_id: str = award_id

    def get_awards_to_collect(self) -> List[BREFAwardToFetch]:
        return get_awards([self.award_id])

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadSpecificAward
