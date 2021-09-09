import requests
from bs4 import BeautifulSoup
import pandas as pd

import constants
from constants import *


class OddsCacheHandler:
    def __init__(self, season):
        self.season = season

    def get_filename(self):
        return odds_files_template % self.season

    def load_file(self, f):
        df = pd.read_html(f.read())[0]
        return df

    def downloader(self):
        to_send = url_address_odds % f"{self.season}-{self.season+1}"
        r = requests.get(to_send)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', {'class': "soh1"})
        try:
            df = pd.read_html(str(table))[0]
        except ValueError:
            with open(constants.missing_files, "a") as f:
                f.write(self.get_filename() + "\n")
            raise ValueError()
        return df

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        f.write(data.to_html())
