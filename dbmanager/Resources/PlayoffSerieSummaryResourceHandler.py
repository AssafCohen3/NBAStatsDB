from alive_progress import alive_it
from sqlalchemy import func, delete
from sqlalchemy.sql import select
from dbmanager.Database.Models.PlayoffSerieSummary import PlayoffSerieSummary
from dbmanager.Handlers.BRPlayoffsSummaryHandler import BRPlayoffsSummaryHandler
from dbmanager.Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert


class PlayoffSerieSummaryResourceHandler(ResourceAbc):

    def __init__(self, session, teams_spans, br_season_links):
        self.teams_spans = teams_spans
        self.br_season_links = br_season_links
        super().__init__(session)

    def get_season_series_fetch_status(self):
        stmt = select(PlayoffSerieSummary.Season, func.min(PlayoffSerieSummary.SerieOrder)).group_by(PlayoffSerieSummary.Season)
        res = self.session.execute(stmt).fetchall()
        return res

    def insert_series(self, series):
        if not series:
            return
        stmt = insert(PlayoffSerieSummary).on_conflict_do_nothing()
        self.session.execute(stmt, series)
        self.session.commit()

    # updates series of a season
    def update_playoff_summary(self, season, season_link):
        handler = BRPlayoffsSummaryHandler(season, season_link, self.teams_spans)
        data = handler.downloader()
        headers = [
            'Season',
            'TeamAId',
            'TeamAName',
            'TeamBId',
            'TeamBName',
            'TeamAWins',
            'TeamBWins',
            'WinnerId',
            'WinnerName',
            'LoserId',
            'LoserName',
            'SerieOrder',
            'LevelTitle'
        ]
        dicts = [dict(zip(headers, serie)) for serie in data]
        self.insert_series(dicts)

    # update all series
    def update_playoffs_summeries(self):
        print('updating playoff sereis')
        fetched_seasons = self.get_season_series_fetch_status()
        # remove series from playoffs that didnt finished to update them later
        for s, order in fetched_seasons:
            if order > 1:
                stmt = delete(PlayoffSerieSummary)\
                    .where(PlayoffSerieSummary.Season == s)
                self.session.execute(stmt)
                self.session.commit()
        fetched_seasons = [s[0] for s in fetched_seasons if s[1] == 1]
        to_fetch = [(season, season_link, league_id) for season, season_link, league_id in self.br_season_links
                    if (league_id == 'BAA' or league_id == 'NBA') and season not in fetched_seasons]
        if len(to_fetch) == 0:
            return
        to_iterate = alive_it(to_fetch, force_tty=True, title="Fetching Playoff series", enrich_print=False, dual_line=True)
        for season, season_link, league_id in to_iterate:
            to_iterate.text(f'-> Fetching {season} playoff series...')
            self.update_playoff_summary(season, season_link)
