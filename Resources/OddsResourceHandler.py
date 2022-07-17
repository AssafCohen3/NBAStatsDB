from alive_progress import alive_it
from sqlalchemy.sql import select
from Database.Models.BoxScoreT import BoxScoreT
from Database.Models.Odds import Odds
from Handlers.OddsHandler import OddsHandler
from Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert
import pandas as pd

from constants import FIRST_ODDS_SEASON, ODDS_TYPES, ODDS_TEAM_NAMES


class OddsResourceHandler(ResourceAbc):

    def insert_odds(self, odds):
        stmt = insert(Odds).on_conflict_do_nothing()
        self.session.execute(stmt, odds)
        self.session.commit()

    # returns the last saved year of odds plus 1 year(empty string if none found)
    def get_last_odds_year(self):
        stmt = select(Odds.Season + 1).order_by(Odds.Season.desc()).limit(1)
        res = self.session.execute(stmt).fetchall()
        return res[0][0] if res else FIRST_ODDS_SEASON

    def get_last_season(self):
        stmt = select(BoxScoreT.Season).where(BoxScoreT.SeasonType == 4).order_by(BoxScoreT.Season.desc()).limit(1)
        last_season = self.session.execute(stmt).fetchall()
        return last_season[0][0] if last_season else None

    # download and saves odds for a season
    def collect_season_odds(self, season):
        handler = OddsHandler(season)
        df = handler.downloader()
        if df is None:
            return
        to_ret = None
        for j, odds_round in enumerate(ODDS_TYPES):
            round_df = df["Team"].join(df["Playoffs,prior to..."][odds_round]).dropna().rename(columns={odds_round: "Odd"})
            round_df["Round"] = 4 - j
            round_df["Season"] = season
            to_ret = round_df if to_ret is None else pd.concat([to_ret, round_df], ignore_index=True)
        to_ret['Team'] = to_ret['Team'].map(ODDS_TEAM_NAMES).fillna(to_ret['Team'])
        to_ret.drop_duplicates(inplace=True)
        self.insert_odds(list(to_ret.to_dict('records')))

    # updates(start form last saved year) odds
    def update_odds(self):
        print('updating odds table...')
        last_saved_season = self.get_last_odds_year()
        last_boxscore_season = self.get_last_season()
        if not last_boxscore_season:
            print('no boxscores in database cant get odds')
        if last_saved_season == last_boxscore_season + 1:
            return
        to_iterate = alive_it(range(last_saved_season, last_boxscore_season + 1), force_tty=True, enrich_print=False, title='Fetching odds', dual_line=True)
        for i in to_iterate:
            to_iterate.text(f'-> downloading odds of season {i}...')
            self.collect_season_odds(i)
