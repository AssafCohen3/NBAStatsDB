# map nba team ids to bref abbrevations by year

import re
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

from constants import BREF_TEAM_NAME_TO_NBA_ID


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
    main()
