import re
from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from bs4 import BeautifulSoup
import pandas as pd

from dbmanager.RequestHandlers.Sessions import timeout_session
from dbmanager.constants import ODDS_ENDPOINT, ODDS_TEAM_NAMES, TEAM_NBA_NAME_TO_NBA_ID, ODDS_ROUNDS


class OddsDownloader(DownloaderAbs):
    def __init__(self, season: int):
        self.season: int = season

    async def download(self):
        to_send = ODDS_ENDPOINT % f"{self.season}-{self.season + 1}"
        r = timeout_session.get(to_send)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', {'class': "soh1"})
        if not table:
            return None
        df = pd.read_html(str(table))[0]
        joined = df["Team"].join(df["Playoffs,prior to..."])
        joined['TeamName'] = [team_name[0].replace('+', ' ')
                              for link in table.select('td  a:first-child')
                              if len((team_name := re.findall(r'https://www\.sportsoddshistory\.com/nba-team/\?sa=nba&Team=(.*)$', link['href']))) > 0]
        joined['TeamName'] = joined['TeamName'].map(ODDS_TEAM_NAMES).fillna(joined['TeamName'])
        joined['TeamId'] = joined['TeamName'].map(TEAM_NBA_NAME_TO_NBA_ID)
        joined = [
            {'TeamId': team_id, 'TeamName': team_name, 'Round': ODDS_ROUNDS[k], 'Odd': v, 'Season': self.season}
            for (team, team_id, team_name), v1 in
            joined.set_index(['Team', 'TeamId', 'TeamName']).transpose().to_dict().items()
            for k, v in v1.items() if pd.notnull(v)]
        return joined
