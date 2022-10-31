import csv
import datetime
import re
from abc import ABC
from dataclasses import dataclass, field
from typing import Type, Dict, Optional, List, Tuple, Union
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import scoped_session
from unidecode import unidecode
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.PlayerMapping import PlayerMapping
from dbmanager.Downloaders import BREFDraftDownloader
from dbmanager.Downloaders.BREFDraftDownloader import BREFDraftDownloader
from dbmanager.Downloaders.BREFPlayerPageDownloader import BREFPlayerPageDownloader
from dbmanager.Downloaders.BREFRookiesDownloader import BREFRookiesDownloader
from dbmanager.Logger import log_message
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.PlayersMappingsActionSpecs import CompleteMissingPlayersMappings, \
    ReadPlayersMappingsFromFile
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SharedData.DefaultMappings import DefaultPlayerMapping, default_mappings
from dbmanager.SharedData.PlayersIndex import PlayerDetails, players_index
from dbmanager.tasks.RetryManager import retry_wrapper


@dataclass
class MappingTarget:
    target_nba_id: int
    target_nba_name: str
    resource_year: int
    resource_type: str
    target_draft_number: Optional[int]


@dataclass
class MappingCandidateLink:
    candidate_bref_id: str
    candidate_bref_name: str
    candidate_bref_link: str
    candidate_draft_number: Optional[int]


@dataclass(unsafe_hash=True)
class TargetResource:
    resource_year: int = field(hash=True)
    resource_type: str = field(hash=True)
    links_to_fetch: int = field(default=0, init=False, compare=False, hash=False)
    resource_targets: Dict[int, MappingTarget] = field(init=False, compare=False, hash=False, default_factory=dict)
    current_link_index: int = field(init=False, default=0)

    def get_target_by_draft_number(self, draft_number: int) -> Optional[MappingTarget]:
        potential_draft_match = [target for target_id, target in self.resource_targets.items() if
                                 target.target_draft_number == draft_number] if self.resource_type == 'draft' else []
        if len(potential_draft_match) > 0:
            return potential_draft_match[0]
        return None


class PlayersMappingActionGeneral(ActionAbc, ABC):
    def insert_mappings(self, mapping: List[Dict]):
        if not mapping:
            return
        insert_stmt = insert(PlayerMapping)
        stmt = insert_stmt.on_conflict_do_update(
            set_={
                c.name: c for c in insert_stmt.excluded
            }
        )
        self.session.execute(stmt, mapping)
        self.session.commit()
        self.update_resource()


class CompleteMissingPlayersMappingsAction(PlayersMappingActionGeneral):
    def __init__(self, session: scoped_session):
        super().__init__(session)
        self.target_resources: List[TargetResource] = []
        self.current_resource_index: int = 0

    def init_task_data_abs(self) -> bool:
        return False

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return CompleteMissingPlayersMappings

    @retry_wrapper
    async def get_player_stats_id(self, candidate: MappingCandidateLink) -> Tuple[int, str]:
        downloader = BREFPlayerPageDownloader(candidate.candidate_bref_id)
        player_resp = downloader.download()
        player_soup = BeautifulSoup(player_resp, 'html.parser')
        player_birth_date = player_soup.select('span#necro-birth')[0]['data-birth']
        nba_stats_links = player_soup.select('#div_stats-nba-com a')
        player_stats_id = None
        for nba_stats_link in nba_stats_links:
            link_href = nba_stats_link['href']
            player_id_regex = re.findall(r'stats.nba.com/player/(.+?)/', link_href)
            if len(player_id_regex) > 0:
                player_stats_id = int(player_id_regex[0])
                break
        return player_stats_id, player_birth_date

    @retry_wrapper
    async def find_season_players_links(self, season: int) -> List[MappingCandidateLink]:
        downloader = BREFRookiesDownloader(season)
        resp = downloader.download()
        soup = BeautifulSoup(resp, 'html.parser')
        player_ids = soup.select('table#rookies tbody tr td[data-stat="player"]')
        candidates = [MappingCandidateLink(p['data-append-csv'],
                                           unidecode(p.select('a')[0].getText().strip()),
                                           'https://www.basketball-reference.com' + p.select('a')[0]['href'],
                                           None)
                      for p in player_ids]
        return candidates

    @retry_wrapper
    async def find_draft_players_links(self, season: int) -> List[MappingCandidateLink]:
        downloader = BREFDraftDownloader(season)
        resp = downloader.download()
        soup = BeautifulSoup(resp, 'html.parser')
        picks = soup.select('table#stats tbody tr')
        current_pick = 1
        to_ret: List[MappingCandidateLink] = []
        for pick in picks:
            if pick.has_attr('class'):
                continue
            player_link_el = pick.select('td[data-stat="player"] a')
            if len(player_link_el) == 0:
                continue
            player_link_el = player_link_el[0]
            player_id = re.findall(r'/players/./(.+?)\.html', player_link_el['href'])[0]
            player_name = unidecode(player_link_el.getText().strip())
            player_link = 'https://www.basketball-reference.com' + player_link_el['href']
            to_ret.append(MappingCandidateLink(player_id, player_name, player_link, current_pick))
            current_pick += 1
        return to_ret

    async def find_targets(self, target_resource: TargetResource, current_bref_mappings: Dict[str, Tuple[int, str]]):
        candidates_links: List[MappingCandidateLink] = await (
            self.find_season_players_links(target_resource.resource_year)
            if target_resource.resource_type == 'season'
            else self.find_draft_players_links(target_resource.resource_year)
        )
        candidates_links = [p for p in candidates_links if p.candidate_bref_id not in current_bref_mappings]  # filter players already mapped
        self.target_resources[self.current_resource_index].links_to_fetch = len(candidates_links)
        await self.finish_subtask()
        for i, candidate_link in enumerate(candidates_links):
            player_stats_id, player_birth_date = await self.get_player_stats_id(candidate_link)
            if not player_stats_id:
                draft_match = target_resource.get_target_by_draft_number(candidate_link.candidate_draft_number)
                if draft_match:
                    player_stats_id = draft_match.target_nba_id
            if player_stats_id and player_stats_id in target_resource.resource_targets:
                new_mapping = {
                    'PlayerNBAId': player_stats_id,
                    'PlayerNBAName': target_resource.resource_targets[player_stats_id].target_nba_name,
                    'PlayerNBABirthDate': None,
                    'PlayerBREFId': candidate_link.candidate_bref_id,
                    'PlayerBREFName': candidate_link.candidate_bref_name,
                    'PlayerBREFBirthDate': datetime.datetime.strptime(player_birth_date, '%Y-%m-%d').date()
                }
                self.insert_mappings([new_mapping])
                target_resource.resource_targets.pop(player_stats_id)
                if len(target_resource.resource_targets.keys()) == 0:
                    self.target_resources[self.current_resource_index].links_to_fetch = i+1
                    await self.finish_subtask()
                    break
            await self.finish_subtask()
        if len(target_resource.resource_targets.keys()) > 0:
            log_message(f'couldnt find mapping for {len(target_resource.resource_targets.keys())} players. consider add it mannualy')
            for player_id, (player_name, _) in target_resource.resource_targets.items():
                log_message(f'\tPlayer Id: {player_id}, Player Name: {player_name}')

    async def action(self):
        current_mappings_stmt = (
            select(PlayerMapping.PlayerNBAId, PlayerMapping.PlayerBREFId)
        )
        current_mapped_players_list: List[Tuple[int, str]] = self.session.execute(current_mappings_stmt).fetchall()
        mapped_nba_players: Dict[int, Tuple[int, str]] = {
            r[0]: r for r in current_mapped_players_list
        }
        all_players: Dict[int, PlayerDetails] = players_index.get_data()
        default_inserts: List[DefaultPlayerMapping] = []
        targets: List[MappingTarget] = []
        for player in all_players.values():
            if player.first_season >= 2022 and not player.played_games_flag and player.draft_year is None:
                # no point at searching new players that hasnt played games
                # since they wont have reference to stats.nba
                continue
            if player.player_id not in mapped_nba_players:
                default_mapping = default_mappings.get_player_mapping(player.player_id)
                if default_mapping:
                    default_inserts.append(default_mapping)
                    continue
                resource_year = player.first_season
                resource_type = 'season'
                draft_number = None
                if player.draft_year is not None:
                    resource_year = player.draft_year
                    resource_type = 'draft'
                    draft_number = player.draft_number
                targets.append(MappingTarget(player.player_id, player.player_name, resource_year, resource_type, draft_number))

        # TODO insert default mappings
        defaults_to_insert: List[Dict] = [
            {
                'PlayerNBAId': m.player_nba_id,
                'PlayerNBAName': m.player_nba_name,
                'PlayerNBABirthDate': m.player_nba_birthdate,
                'PlayerBREFId': m.player_bref_id,
                'PlayerBREFName': m.player_bref_name,
                'PlayerBREFBirthDate': m.player_bref_birthdate
            } for m in default_inserts
        ]
        self.insert_mappings(defaults_to_insert)
        current_mapped_players_list: List[Tuple[int, str]] = self.session.execute(current_mappings_stmt).fetchall()
        mapped_bref_players: Dict[str, Tuple[int, str]] = {
            r[1]: r for r in current_mapped_players_list
        }
        resources_to_fetch: Dict[TargetResource, TargetResource] = {}
        for target in targets:
            resource_target = TargetResource(target.resource_year, target.resource_type)
            if resource_target in resources_to_fetch:
                resource_target = resources_to_fetch[resource_target]
            else:
                resources_to_fetch[resource_target] = resource_target
            resource_target.resource_targets[target.target_nba_id] = target
        self.target_resources = list(resources_to_fetch.values())
        for i, target_resource in enumerate(self.target_resources):
            self.current_resource_index = i
            await self.find_targets(target_resource, mapped_bref_players)

    def get_current_subtask_text_abs(self) -> str:
        # searching targets of resource {type} of season {season}
        return gettext('resources.players_mappings.actions.complete_missing_players_mappings.fetching_candidate',
                       type=self.target_resources[self.current_resource_index].resource_type if self.current_resource_index < len(self.target_resources) else '',
                       season=self.target_resources[self.current_resource_index].resource_year if self.current_resource_index < len(self.target_resources) else '')

    def subtasks_count(self) -> Union[int, None]:
        to_ret = len(self.target_resources)
        for resource_targe in self.target_resources:
            to_ret += resource_targe.links_to_fetch
        return to_ret


class ReadPlayersMappingsFromFileAction(PlayersMappingActionGeneral):
    def __init__(self, session: scoped_session, file_path: str):
        super().__init__(session)
        self.file_path = file_path

    def init_task_data_abs(self) -> bool:
        return False

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return ReadPlayersMappingsFromFile

    async def action(self):
        mappings = []
        with open(self.file_path, encoding='ISO-8859-1') as f:
            csvreader = csv.reader(f, )
            headers = next(csvreader)
            bref_id_idx = headers.index('PlayerBREFId')
            bref_name_idx = headers.index('PlayerBREFName')
            bref_birthdate_idx = headers.index('PlayerBREFBirthDate')
            nba_id_idx = headers.index('PlayerNBAId')
            nba_name_idx = headers.index('PlayerNBAName')
            nba_birthdate_idx = headers.index('PlayerNBABirthDate')
            for p in csvreader:
                mappings.append({
                    'PlayerNBAId': int(p[nba_id_idx]),
                    'PlayerNBAName': p[nba_name_idx],
                    'PlayerNBABirthDate': datetime.date.fromisoformat(p[nba_birthdate_idx]) if p[nba_birthdate_idx] != '' else None,
                    'PlayerBREFId': p[bref_id_idx],
                    'PlayerBREFName': p[bref_name_idx],
                    'PlayerBREFBirthDate': datetime.date.fromisoformat(p[bref_birthdate_idx]) if p[bref_birthdate_idx] != '' else None
                })
        self.insert_mappings(mappings)
        await self.finish_subtask()

    def get_current_subtask_text_abs(self) -> str:
        # Loading players mappings from file
        return gettext('resources.players_mappings.actions.read_players_mappings_from_file.loading_mappings_from_file')

    def subtasks_count(self) -> Union[int, None]:
        return 1
