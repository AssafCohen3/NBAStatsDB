import datetime
import logging
import re
from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from bs4 import BeautifulSoup

from dbmanager.RequestHandlers.Sessions import bref_session
from dbmanager.SharedData.BREFSeasonsLinks import BREFSeasonLink
from dbmanager.constants import BREF_ABBREVATION_TO_NBA_TEAM_ID, TEAM_NBA_ID_TO_NBA_NAME, BREF_LEVEL_TITLE_TO_ORDER, \
    BREF_PLAYOFFS_URL


class BREFPlayoffSeriesDownloader(DownloaderAbs):
    def __init__(self, season_link: BREFSeasonLink):
        self.season_link = season_link

    async def download(self):
        to_send = BREF_PLAYOFFS_URL % (self.season_link.leagu_id, self.season_link.season+1)
        r = await bref_session.async_get(to_send)
        if r.status_code == 404:
            return None
        return self.from_html(r.text)

    def from_html(self, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        series_rows = soup.select('table#all_playoffs tbody > tr')
        to_ret = []
        row_index = 0
        while row_index < len(series_rows):
            row = series_rows[row_index]
            if row.has_attr('class'):
                if 'thead' not in row['class'] and 'foo-bar' not in row['class']:
                    raise Exception('what')
                row_index += 1
                continue
            level_description = row.select('span strong')
            if not level_description:
                row_index += 1
                continue
            level_description = level_description[0].getText()
            if 'Tiebreaker' in level_description:
                row_index += 2
                continue
            elif 'Round Robin' in level_description:
                row_index += 1
                continue
            summary_col = row.select('td')[1]
            status = summary_col.contents[1].getText().strip()
            if status not in ['over', 'lead', 'trail', 'tied with']:
                logging.info(f'found new series status: {status}')
            is_over = 1 if status == 'over' else 0
            teams_tags = summary_col.select('a')
            winner_bref_abbr = re.findall(r'/teams/(.+?)/', teams_tags[0]['href'])[0]
            loser_bref_abbr = re.findall(r'/teams/(.+?)/', teams_tags[1]['href'])[0]
            winner_candidates = BREF_ABBREVATION_TO_NBA_TEAM_ID[winner_bref_abbr]
            loser_candidates = BREF_ABBREVATION_TO_NBA_TEAM_ID[loser_bref_abbr]
            winner_id = [c for c in winner_candidates if c[0] <= self.season_link.season <= c[1]][0][2]
            loser_id = [c for c in loser_candidates if c[0] <= self.season_link.season <= c[1]][0][2]
            winner_name = TEAM_NBA_ID_TO_NBA_NAME[winner_id]
            loser_name = TEAM_NBA_ID_TO_NBA_NAME[loser_id]
            results = summary_col.contents[-1].getText().strip().replace('(', '').replace(')', '').split('-')
            winner_wins = int(results[0])
            loser_wins = int(results[1])
            serie_order = self.get_level_order(level_description)
            team_a_id, team_a_name, team_a_wins, team_b_id, team_b_name, team_b_wins = (winner_id, winner_name, winner_wins, loser_id, loser_name, loser_wins) if winner_id < loser_id else (loser_id, loser_name, loser_wins, winner_id, winner_name, winner_wins)
            games_table_row = series_rows[row_index+1]
            games_links = games_table_row.select('table tbody tr td a')
            if len(games_links) == 0:
                first_game_date = None
                last_game_date = None
            else:
                first_game = games_links[0]
                last_game = games_links[-1]
                first_game_link = first_game['href']
                first_game_date_str = re.findall(r'/boxscores/([0-9]{8})', first_game_link)[0]
                first_game_date = datetime.datetime.strptime(first_game_date_str, '%Y%m%d').date()
                last_game_link = last_game['href']
                last_game_date_str = re.findall(r'/boxscores/([0-9]{8})', last_game_link)[0]
                last_game_date = datetime.datetime.strptime(last_game_date_str, '%Y%m%d').date()
            to_ret.append([self.season_link.season,
                           team_a_id, team_a_name, team_b_id, team_b_name,
                           team_a_wins, team_b_wins,
                           winner_id, winner_name, loser_id, loser_name,
                           serie_order, level_description,
                           first_game_date, last_game_date,
                           is_over])
            row_index += 2
        return to_ret

    def get_level_order(self, level_description):
        return [order for first_season, last_season, order in BREF_LEVEL_TITLE_TO_ORDER[level_description] if first_season <= self.season_link.season <= last_season][0]
