# map nba team ids to bref abbrevations by year

import re
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

from dbmanager.constants import BREF_TEAM_NAME_TO_NBA_ID, BREF_DEFUNCT_TEAM_NAME_NBA_ID, TEAM_NBA_ID_TO_NBA_NAME


def abbrevation_to_team_id():
    team_index_url = 'https://www.basketball-reference.com/teams/'
    resp = requests.get(team_index_url).text
    soup = BeautifulSoup(resp, 'html.parser')
    team_links = soup.select('table#teams_active tbody tr th[data-stat="franch_name"] a')
    team_links = [[link, False] for link in team_links]
    defunct_team_links = soup.select('table#teams_defunct tbody tr')
    for def_team in defunct_team_links:
        lg_id = def_team.select('td[data-stat="lg_id"]')
        franch_name = def_team.select('th[data-stat="franch_name"] a')
        if len(lg_id) > 0 and len(franch_name) > 0 and ('BAA' in lg_id[0].getText() or 'NBA' in lg_id[0].getText()):
            team_links.insert(0, [franch_name[0], True])
    team_links = [[tl.get_text().strip(), 'https://www.basketball-reference.com' + tl['href'], is_defunct] for tl, is_defunct in team_links]
    abbrevations_list = []
    for franchise_bref_name, team_link, is_defunct in team_links:
        franchise_nba_id = BREF_TEAM_NAME_TO_NBA_ID[franchise_bref_name] if not is_defunct else BREF_DEFUNCT_TEAM_NAME_NBA_ID[franchise_bref_name]
        franchise_nba_name = TEAM_NBA_ID_TO_NBA_NAME[franchise_nba_id]
        print(f'fetching {franchise_bref_name}...')
        team_seasons_resp = requests.get(team_link).text
        team_seasons_soup = BeautifulSoup(team_seasons_resp, 'html.parser')
        seasons_rows = team_seasons_soup.select('table.stats_table tbody tr', {'class': ''})
        relevant_rows = []
        for season_row in seasons_rows:
            lg_id = season_row.select('[data-stat="lg_id"] a')[0].getText()
            if lg_id == 'NBA' or lg_id == 'BAA':
                relevant_rows.append(season_row)
        seasons_links = [s.select('[data-stat="season"] a')[0] for s in relevant_rows]
        seasons = [[int(sl.get_text().split('-')[0]), re.findall(r'^/teams/(.*?)/\d*\.html$', sl['href'])[0]] for sl in seasons_links]
        prev_abbr_to_insert = None
        sorted_seasons = sorted(seasons, key=lambda s: s[0])
        # start end team_id abbr
        for i, (season, bref_abbr) in enumerate(sorted_seasons):
            if prev_abbr_to_insert is None or bref_abbr != prev_abbr_to_insert[4]:
                prev_abbr_to_insert = [season, None, franchise_nba_id, franchise_nba_name, bref_abbr]
                abbrevations_list.append(prev_abbr_to_insert)
            if prev_abbr_to_insert is not None:
                prev_abbr_to_insert[1] = season
        if not is_defunct:
            prev_abbr_to_insert[1] = 3000 - 1
    abbrevations_changes = defaultdict(list)
    abbrevations_list = sorted(abbrevations_list)
    for start_season, end_season, team_nba_id, team_nba_name, team_bref_abbr in abbrevations_list:
        if team_bref_abbr in abbrevations_changes:
            last_occurence = abbrevations_changes[team_bref_abbr][-1][1]
            if start_season <= last_occurence:
                raise Exception('ffff')
        abbrevations_changes[team_bref_abbr].append([start_season, end_season, team_nba_id, team_nba_name])
    print(dict(abbrevations_changes))


def main():
    team_index_url = 'https://www.basketball-reference.com/teams/'
    resp = requests.get(team_index_url).text
    soup = BeautifulSoup(resp, 'html.parser')
    team_links = soup.select('table#teams_active tbody tr th[data-stat="franch_name"] a')
    team_links = [[tl.get_text().strip(), 'https://www.basketball-reference.com' + tl['href']] for tl in team_links]
    teams_changes = defaultdict(list)
    for franchise_name, team_link in team_links:
        franchise_id = BREF_TEAM_NAME_TO_NBA_ID[franchise_name]
        print(f'fetching {franchise_name}...')
        team_seasons_resp = requests.get(team_link).text
        team_seasons_soup = BeautifulSoup(team_seasons_resp, 'html.parser')
        seasons_rows = team_seasons_soup.select('table.stats_table tbody tr', {'class': ''})
        seasons_links = [s.select('[data-stat="season"] a')[0] for s in seasons_rows]
        seasons = [[int(sl.get_text().split('-')[0]), re.findall(r'^/teams/(.*?)/\d*\.html$', sl['href'])[0]] for sl in seasons_links]
        prev_abbr = None
        sorted_seasons = sorted(seasons, key=lambda s: s[0])
        for i, (season, abbr) in enumerate(sorted_seasons):
            if prev_abbr is None or abbr != prev_abbr:
                if prev_abbr is not None:
                    teams_changes[franchise_id][-1][1] = season - 1
                teams_changes[franchise_id].append([season, None, abbr])
            prev_abbr = abbr
        teams_changes[franchise_id][-1][1] = 3000
    print(dict(teams_changes))


if __name__ == '__main__':
    abbrevation_to_team_id()
