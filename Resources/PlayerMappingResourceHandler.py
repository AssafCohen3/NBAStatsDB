import csv
import re
from collections import defaultdict
from datetime import datetime
from alive_progress import alive_it
from MainRequestsSession import requests_session as requests
from bs4 import BeautifulSoup
from sqlalchemy import union, func, literal_column
from sqlalchemy.sql import select
from unidecode import unidecode
from Database.Models.BoxScoreP import BoxScoreP
from Database.Models.Player import Player
from Database.Models.PlayerMapping import PlayerMapping
from Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert


class PlayerMappingResourceHandler(ResourceAbc):

    def insert_mappings(self, mappings):
        insert_stmt = insert(PlayerMapping)
        stmt = insert_stmt.on_conflict_do_update(
            set_={
                c.name: c for c in insert_stmt.excluded
            }
        )
        self.session.execute(stmt, mappings)
        self.session.commit()

    def load_players_ids_mapping(self):
        print('loading initial mappings from file')
        with open('players_ids/players.csv', encoding='ISO-8859-1') as f:
            csvreader = csv.reader(f, )
            headers = next(csvreader)
            bref_id_idx = headers.index('PlayerBREFId')
            bref_name_idx = headers.index('PlayerBREFName')
            bref_birthdate_idx = headers.index('PlayerBREFBirthDate')
            nba_id_idx = headers.index('PlayerNBAId')
            nba_name_idx = headers.index('PlayerNBAName')
            nba_birthdate_idx = headers.index('PlayerNBABirthDate')
            to_insert = []
            for p in csvreader:
                if p[bref_id_idx] != 'NA' and p[nba_id_idx] != 'NA':
                    to_insert.append({
                        'PlayerNBAId': int(p[nba_id_idx]),
                        'PlayerNBAName': unidecode(p[nba_name_idx]) if p[nba_name_idx] != '' else None,
                        'PlayerNBABirthDate': datetime.fromisoformat(p[nba_birthdate_idx]).date() if p[nba_birthdate_idx] != '' else None,
                        'PlayerBREFId': p[bref_id_idx],
                        'PlayerBREFName': unidecode(p[bref_name_idx]) if p[bref_name_idx] != '' else None,
                        'PlayerBREFBirthDate': datetime.fromisoformat(p[bref_birthdate_idx]).date() if p[bref_birthdate_idx] != '' else None
                    })
            self.insert_mappings(to_insert)

    @staticmethod
    def get_player_stats_id(player_url):
        player_resp = requests.get(player_url).text
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

    @staticmethod
    def find_season_players_links(season):
        url = 'https://www.basketball-reference.com/leagues/NBA_%s_rookies.html' % (season + 1)
        resp = requests.get(url).text
        soup = BeautifulSoup(resp, 'html.parser')
        player_ids = soup.select('table#rookies tbody tr td[data-stat="player"]')
        player_ids = [(p['data-append-csv'],
                       unidecode(p.select('a')[0].getText().strip()),
                       'https://www.basketball-reference.com' + p.select('a')[0]['href'],
                       None) for p in player_ids]
        return player_ids

    @staticmethod
    def find_draft_players_links(season):
        url = 'https://www.basketball-reference.com/draft/NBA_%s.html' % season
        resp = requests.get(url).text
        soup = BeautifulSoup(resp, 'html.parser')
        picks = soup.select('table#stats tbody tr')
        current_pick = 1
        to_ret = []
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
            to_ret.append([player_id, player_name, player_link, current_pick])
            current_pick += 1
        return to_ret

    def find_targets(self, resource_year, resource_type, target_ids, current_mappings):
        resource_players_links = self.find_season_players_links(
            resource_year) if resource_type == 'season' else self.find_draft_players_links(resource_year)
        resource_players_links = [p for p in resource_players_links if p[0] not in current_mappings]  # filter players already mapped
        to_ret = []
        print(f'fetching {len(resource_players_links)} players from {resource_type} {resource_year}. targeting {len(target_ids.keys())} players...')
        if len(resource_players_links) == 0:
            return
        to_iterate = alive_it(resource_players_links, force_tty=True, enrich_print=False, title='Mapping BREF Players', dual_line=True)
        for player_id, player_name, player_link, player_drat_pick in to_iterate:
            to_iterate.text(f'-> Fetching {player_name} stats.nba id...')
            player_stats_id, player_birth_date = self.get_player_stats_id(player_link)
            if not player_stats_id:
                potential_draft_match = [k for k, a in target_ids.items() if a[1] == player_drat_pick] if resource_type == 'draft' else []
                if len(potential_draft_match) > 0:
                    player_stats_id = potential_draft_match[0]
            if player_stats_id and player_stats_id in target_ids:
                to_ret.append(
                    {
                        'PlayerNBAId': player_stats_id,
                        'PlayerNBAName': target_ids[player_stats_id][0],
                        'PlayerNBABirthDate': None,
                        'PlayerBREFId': player_id,
                        'PlayerBREFName': player_name,
                        'PlayerBREFBirthDate': datetime.strptime(player_birth_date, '%Y-%m-%d').date()
                    })
                target_ids.pop(player_stats_id)
                if len(target_ids.keys()) == 0:
                    break
        if len(target_ids.keys()) > 0:
            print(f'couldnt find mapping for {len(target_ids.keys())} players. consider add it mannualy')
            for player_id, (player_name, _) in target_ids.items():
                print(f'\tPlayer Id: {player_id}, Player Name: {player_name}')
        return to_ret

    def try_to_complete_missing_mapping(self):
        print('trying to complete missing mappings')
        all_players_ids_cte = union(
            select(BoxScoreP.PlayerId).distinct(),
            select(Player.PlayerId).distinct()
        ).cte()
        missing_players_cte = (
            select(all_players_ids_cte.c.PlayerId).
            outerjoin(PlayerMapping, PlayerMapping.PlayerNBAId == all_players_ids_cte.c.PlayerId).
            where(PlayerMapping.PlayerNBAId.is_(None)).
            cte()
        )
        joined = (
            missing_players_cte.
            outerjoin(BoxScoreP, missing_players_cte.c.PlayerId == BoxScoreP.PlayerId).
            outerjoin(Player, missing_players_cte.c.PlayerId == Player.PlayerId)
        )
        stmt = (
            select(missing_players_cte.c.PlayerId,
                   func.coalesce(BoxScoreP.PlayerName, Player.FullName),
                   func.coalesce(func.min(BoxScoreP.Season), Player.DraftYear).label('ResourceYear'),
                   func.iif(func.min(BoxScoreP.Season).is_(None), 'draft', 'season'),
                   Player.DraftNumber).
            select_from(joined).
            group_by(missing_players_cte.c.PlayerId).
            having(~literal_column('ResourceYear').is_(None))
        )
        missing_mapping = self.session.execute(stmt).fetchall()
        current_mappings = self.session.execute(select(PlayerMapping.PlayerBREFId)).fetchall()
        current_mappings = set([m[0] for m in current_mappings])

        resources_to_fetch = defaultdict(dict)
        for missing_player_id, missing_player_name, resource_year, resource_type, draft_pick in missing_mapping:
            resources_to_fetch[(resource_year, resource_type)][missing_player_id] = (missing_player_name, draft_pick)
        for (resource_year, resource_type), targets in resources_to_fetch.items():
            new_mappings = self.find_targets(resource_year, resource_type, targets, current_mappings)
            self.insert_mappings(new_mappings)

    def update_mappings_table(self):
        print('updating mapping table')
        self.load_players_ids_mapping()
        self.try_to_complete_missing_mapping()
