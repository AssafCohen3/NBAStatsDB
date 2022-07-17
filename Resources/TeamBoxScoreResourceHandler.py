import re
import time
from collections import defaultdict
from datetime import datetime

from sqlalchemy.sql import select

from Database.Models.BoxScoreT import BoxScoreT
from Handlers.BoxScoreHandler import BoxScoreHandler
from Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert
from constants import SEASON_TYPES, API_COUNT_THRESHOLD, STATS_DELAY_SECONDS


class TeamBoxScoreResourceHandler(ResourceAbc):
    @staticmethod
    def transform_boxscores(rows, headers):
        renames = {
            'TEAM_ID': 'TeamId',
            'TEAM_ABBREVIATION': 'TeamAbbreviation',
            'TEAM_NAME': 'TeamName',
            'GAME_ID': 'GameId',
            'GAME_DATE': 'GameDate',
            'MATCHUP': 'Matchup',
            'PLUS_MINUS': 'PlusMinus',
            'VIDEO_AVAILABLE': 'VideoAvailable'
        }

        def get_row_dict(row):
            to_ret = dict(zip(headers, row))
            to_ret['IsHome'] = 0 if '@' in to_ret['Matchup'] else 1
            season_and_type = re.findall(r'(\d)(\d*)', to_ret["SEASON_ID"])[0]
            to_ret["SeasonType"] = int(season_and_type[0])
            to_ret["Season"] = int(season_and_type[1])
            to_ret['GameDate'] = datetime.strptime(to_ret['GameDate'], '%Y-%m-%d').date()
            to_ret.pop('SEASON_ID')
            return to_ret

        headers = [renames[h] if h in renames else h for h in headers]
        initial_dicts = [get_row_dict(row) for row in rows]
        games_dict = defaultdict(list)
        for d in initial_dicts:
            games_dict[d['GameId']].append(d)
        for game_id, teams in games_dict.items():
            team_a, team_b = sorted(teams, key=lambda t: t['TeamId'])
            team_a_id, team_a_name, team_b_id, team_b_name = team_a['TeamId'], team_a['TeamName'], team_b['TeamId'], team_b['TeamName']
            team_a['TeamAId'] = team_b['TeamAId'] = team_a_id
            team_a['TeamAName'] = team_b['TeamAName'] = team_a_name
            team_a['TeamBId'] = team_b['TeamBId'] = team_b_id
            team_a['TeamBName'] = team_b['TeamBName'] = team_b_name
        return initial_dicts

    # returns the last saved date of some box score type plus 1 day(empty string if none found)
    def get_last_game_date(self, seaseon_type_code):
        stmt = select(BoxScoreT.GameDate).where(BoxScoreT.SeasonType == seaseon_type_code).order_by(BoxScoreT.GameDate.desc()).limit(1)
        res = self.session.execute(stmt).fetchall()
        return res[0][0] if res else ''

    def insert_boxscores(self, boxscores):
        stmt = insert(BoxScoreT).on_conflict_do_nothing()
        self.session.execute(stmt, boxscores)
        self.session.commit()

    def save_boxscores(self, boxscores_rows, headers):
        if not boxscores_rows:
            return
        to_save = self.transform_boxscores(boxscores_rows, headers)
        self.insert_boxscores(to_save)

    # download and saves all box scores of a type from a date or from the begining
    def collect_all_season_type_boxscores(self, season_type_index, start_date=''):
        date_from = start_date
        continue_loop = True
        while continue_loop:
            data = BoxScoreHandler(date_from, season_type_index, 'T').downloader()
            if not data:
                break
            data = data["resultSets"][0]
            headers = data["headers"]
            results = data["rowSet"]
            print(f"found {len(results)} teams boxscores in {SEASON_TYPES[season_type_index]['name'].replace('+', ' ')} from date {date_from}")
            game_date_index = headers.index("GAME_DATE")
            wl_index = headers.index('WL')
            if len(results) >= API_COUNT_THRESHOLD:
                count = 0
                last_date = results[-1][game_date_index]
                while results[-1][game_date_index] == last_date:
                    results.pop()
                    count = count+1
                date_from = last_date
            else:
                continue_loop = False
            # take only boxscores that occured in the past(5 days should be enough i guess) or finished(WL is not null)
            results = [r for r in results if r[wl_index] is not None or (datetime.now() - datetime.strptime(r[game_date_index], '%Y-%m-%d')).days >= 5]
            self.save_boxscores(results, headers)
            time.sleep(STATS_DELAY_SECONDS)  # sleep to prevent ban

    # updates(starts from the last saved date) all box scores of all season types of box score type
    def update_boxscores_table(self):
        print(f'updating teams boxscores')
        for i in range(0, len(SEASON_TYPES)):
            last_date = self.get_last_game_date(SEASON_TYPES[i]['code'])
            print(f'updating teams boxscores and season type {SEASON_TYPES[i]["name"]}... current last saved date: {last_date if last_date else "None"}')
            self.collect_all_season_type_boxscores(i, start_date=last_date)
