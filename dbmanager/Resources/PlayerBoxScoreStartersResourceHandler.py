from collections import defaultdict
from alive_progress import alive_it
from sqlalchemy import update, bindparam, and_
from sqlalchemy.sql import select
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Downloaders.BREFStartersHandler import BREFStartersHandler
from dbmanager.Resources.ResourceAbc import ResourceAbc


class PlayerBoxScoreStartersResourceHandler(ResourceAbc):
    def __init__(self, bref_players_map, session):
        super().__init__(session)
        self.bref_players_map = bref_players_map

    def update_boxscores_starters_all(self, games_ids, games_with_starters):
        if not games_ids or not games_with_starters:
            return
        update_starters_stmt = (
            update(BoxScoreP).
            where(and_(
                BoxScoreP.PlayerId == bindparam('RowPlayerId'),
                BoxScoreP.GameId == bindparam('RowGameId'),
                BoxScoreP.TeamId == bindparam('RowTeamId'),
                BoxScoreP.Starter.is_(None)
            )).
            values(
                Starter=1
            )
        )
        update_bench_stmt = (
            update(BoxScoreP).
            where(and_(
                BoxScoreP.GameId == bindparam('RowGameId'),
                BoxScoreP.TeamId == bindparam('RowTeamId'),
                BoxScoreP.Starter.is_(None)
            )).
            values(
                Starter=0
            )
        )
        self.session.execute(update_starters_stmt, games_with_starters)
        self.session.execute(update_bench_stmt, games_ids)
        self.session.commit()

    def get_teams_seasons_without_starters(self):
        # TODO: for now basketball reference starting lineups not contains play in lineups.
        stmt = (
            select(BoxScoreP.Season, BoxScoreP.TeamId, BoxScoreP.TeamName, BoxScoreP.GameDate, BoxScoreP.GameId).
            where(and_(BoxScoreP.Season >= 1983, BoxScoreP.SeasonType.in_([2, 4]), BoxScoreP.Starter.is_(None))).
            order_by(BoxScoreP.Season, BoxScoreP.TeamId)
        )
        res = self.session.execute(stmt).fetchall()
        to_ret = defaultdict(dict)
        for season, team_id, team_name, game_date, game_id in res:
            key = (season, team_id, team_name)
            to_ret[key][str(game_date)] = game_id
        to_ret = [[season, team_id, team_name, mapped_games] for (season, team_id, team_name), mapped_games in to_ret.items()]
        return to_ret

    def collect_bref_starters(self):
        print('updating startes...')
        missing_seasons = self.get_teams_seasons_without_starters()
        print(f'collecting starters from {len(missing_seasons)} seasons of teams...')
        if len(missing_seasons) == 0:
            return
        to_iterate = alive_it(missing_seasons, force_tty=True, enrich_print=False, title='Fetching Teams Starters', dual_line=True)
        for season, team_id, team_name, games_dates_to_ids in to_iterate:
            to_iterate.text(f'-> Fetching {season} {team_name} starters...')
            handler = BREFStartersHandler(season, team_id, self.bref_players_map)
            games_with_starters = handler.downloader()
            to_update = [{
                'RowPlayerId': starter_id,
                'RowGameId': games_dates_to_ids[game_date],
                'RowTeamId': team_id
            } for game_date, starters_ids in games_with_starters for starter_id in starters_ids if game_date in games_dates_to_ids]
            to_update_game_ids = [{
                'RowGameId': games_dates_to_ids[game_date],
                'RowTeamId': team_id
            } for game_date, starters_ids in games_with_starters if game_date in games_dates_to_ids]
            self.update_boxscores_starters_all(to_update_game_ids, to_update)
