import json

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import stats_session
from dbmanager.constants import NBA_STARTERS_ENDPOINT, START_POSITIONS


class NBAStartersDownloader(DownloaderAbs):
    def __init__(self, game_id: str) -> None:
        super().__init__()
        self.game_id = game_id

    async def download(self):
        url = NBA_STARTERS_ENDPOINT % self.game_id
        resp = await stats_session.async_get(url)
        data = json.loads(resp.text)
        data = data['resultSets'][0]
        headers = data['headers']
        data = data['rowSet']
        player_id_index = headers.index('PLAYER_ID')
        team_id_index = headers.index('TEAM_ID')
        position_index = headers.index('START_POSITION')
        starters = [(self.game_id, r[team_id_index], r[player_id_index])
                    for r in data if r[position_index] in START_POSITIONS]
        if len(starters) != 10:
            raise Exception(f'wtf game {self.game_id}, starters: {", ".join(list(map(str,starters)))}')
        games = set(s[:-1] for s in starters)
        return starters, games

