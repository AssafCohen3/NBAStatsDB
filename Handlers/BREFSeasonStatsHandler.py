import json
import re
import unidecode
import requests
from bs4 import BeautifulSoup
import pandas as pd
from constants import *


class BREFSeasonStatsHandler:
    def __init__(self, season, leage):
        self.season = season
        self.league = leage
        self.resp = None

    def get_filename(self):
        return BREF_SEASON_STATS_FILE_TEMPLATE % (self.league, self.season)

    def load_file(self, f):
        return self.from_html(f.read())

    def downloader(self):
        to_send = BREF_SEASON_STATS_ENDPOINT % (self.league, self.season + 1)
        r = requests.get(to_send)
        self.resp = r.text
        return self.from_html(r.text)

    def from_html(self, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        table = soup.find('table')
        df = pd.read_html(str(table))[0]
        player_ids = [col.get('data-append-csv') for row in table.find_all('tr', {'class': 'full_table'}) for
                      col in row.find_all('td', {'data-stat': 'player'})]
        player_names = [unidecode.unidecode(str(col.find("a").get_text(strip=True))) for row in
                        table.find_all('tr', {'class': 'full_table'}) for col in
                        row.find_all('td', {'data-stat': 'player'})]
        # get rid of multiple teams in one seasons for one player
        df.drop_duplicates(['Rk'], inplace=True)
        # drop rank
        df.drop(['Rk'], inplace=True, axis=1)
        # drop Player row
        df.drop(df[df.G == 'G'].index, inplace=True)
        # replace names
        df.insert(loc=0, column='PlayerName', value= player_names)
        # insert player_ids
        df.insert(loc=1, column='PlayerId', value=player_ids)
        # insert year
        df.insert(loc=2, column='Season', value=self.season)
        # insert league
        df.insert(loc=3, column='League', value=self.league)
        to_ret = df[['PlayerId', 'PlayerName', 'Season', 'League']]
        a = list(to_ret.to_records(index=False))
        return a

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        f.write(self.resp)
