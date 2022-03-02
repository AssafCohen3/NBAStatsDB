from pathlib import Path

import requests
from bs4 import BeautifulSoup
import pandas as pd

import constants
from constants import *


class OddsCacheHandler:
    def __init__(self, season):
        self.season = season

    def get_filename(self):
        return ODDS_FILE_TEMPLATE % self.season

    def load_file(self, f):
        df = pd.read_html(f.read())[0]
        return df

    def downloader(self):
        to_send = ODDS_ENDPOINT % f"{self.season}-{self.season + 1}"
        r = requests.get(to_send)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', {'class': "soh1"})
        df = pd.read_html(str(table))[0]
        return df

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        f.write(data.to_html())
