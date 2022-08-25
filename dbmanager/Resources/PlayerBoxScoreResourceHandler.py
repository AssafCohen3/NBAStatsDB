import re
import time
from collections import defaultdict
from datetime import datetime
from sqlalchemy.sql import select
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Handlers.BoxScoreHandler import BoxScoreHandler
from dbmanager.Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert
from dbmanager.constants import SEASON_TYPES, API_COUNT_THRESHOLD, STATS_DELAY_SECONDS


class PlayerBoxScoreResourceHandler(ResourceAbc):

    @staticmethod
    def transform_boxscores(rows, headers):
        renames = {
            'PLAYER_ID': 'PlayerId',
            'PLAYER_NAME': 'PlayerName',
            'TEAM_ID': 'TeamId',
            'TEAM_ABBREVIATION': 'TeamAbbreviation',
            'TEAM_NAME': 'TeamName',
            'GAME_ID': 'GameId',
            'GAME_DATE': 'GameDate',
            'MATCHUP': 'Matchup',
            'PLUS_MINUS': 'PlusMinus',
            'FANTASY_PTS': 'FantasyPts',
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
        games_dict = defaultdict(lambda: defaultdict(list))
        for d in initial_dicts:
            games_dict[d['GameId']][d['TeamId']].append(d)
        for game_id, teams_dict in games_dict.items():
            team_a_id, team_b_id = sorted(teams_dict.keys())
            team_a_name, team_b_name = teams_dict[team_a_id][0]['TeamName'], teams_dict[team_b_id][0]['TeamName']
            for t in teams_dict.values():
                for p in t:
                    p['TeamAId'] = team_a_id
                    p['TeamAName'] = team_a_name
                    p['TeamBId'] = team_b_id
                    p['TeamBName'] = team_b_name
        return initial_dicts

    # returns the last saved date of some box score type plus 1 day(empty string if none found)
    def get_last_game_date(self, seaseon_type_code):
        stmt = select(BoxScoreP.GameDate).where(BoxScoreP.SeasonType == seaseon_type_code).order_by(BoxScoreP.GameDate.desc()).limit(1)
        res = self.session.execute(stmt).fetchall()
        return res[0][0] if res else ''

    def insert_boxscores(self, boxscores):
        if not boxscores:
            return
        stmt = insert(BoxScoreP).on_conflict_do_nothing()
        self.session.execute(stmt, boxscores)
        self.session.commit()

    def save_boxscores(self, boxscores_rows, headers):
        to_save = self.transform_boxscores(boxscores_rows, headers)
        self.insert_boxscores(to_save)

    # download and saves all box scores of a type from a date or from the begining
    def collect_all_season_type_boxscores(self, season_type_index, start_date=''):
        date_from = start_date
        continue_loop = True
        while continue_loop:
            data = BoxScoreHandler(date_from, season_type_index, 'P').downloader()
            if not data:
                break
            data = data["resultSets"][0]
            headers = data["headers"]
            results = data["rowSet"]
            print(f"found {len(results)} players boxscores in {SEASON_TYPES[season_type_index]['name'].replace('+', ' ')} from date {date_from}")
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
        print(f'updating players boxscores')
        for i in range(0, len(SEASON_TYPES)):
            last_date = self.get_last_game_date(SEASON_TYPES[i]['code'])
            print(f'updating players boxscores and season type {SEASON_TYPES[i]["name"]}... current last saved date: {last_date if last_date else "None"}')
            self.collect_all_season_type_boxscores(i, start_date=last_date)
