from sqlalchemy.sql import select
from dbmanager.Database.Models.BoxScoreT import BoxScoreT
from dbmanager.Database.Models.Player import Player
from dbmanager.Downloaders.PlayersHandler import PlayersHandler
from dbmanager.Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert


class PlayerResourceHandler(ResourceAbc):

    def get_last_season(self):
        stmt = select(BoxScoreT.Season).where(BoxScoreT.SeasonType == 4).order_by(BoxScoreT.Season.desc()).limit(1)
        last_season = self.session.execute(stmt).fetchall()
        return last_season[0][0] if last_season else None

    def insert_players(self, players):
        if not players:
            return
        insert_stmt = insert(Player)
        stmt = insert_stmt.on_conflict_do_update(
            set_={
                'FirstName': insert_stmt.excluded.FirstName,
                'LastName': insert_stmt.excluded.LastName,
                'PlayerSlug': insert_stmt.excluded.PlayerSlug,
                'Active': insert_stmt.excluded.Active,
                'Position': insert_stmt.excluded.Position,
                'Height': insert_stmt.excluded.Height,
                'Weight': insert_stmt.excluded.Weight,
                'College': insert_stmt.excluded.College,
                'Country': insert_stmt.excluded.Country,
                'DraftYear': insert_stmt.excluded.DraftYear,
                'DraftRound': insert_stmt.excluded.DraftRound,
                'DraftNumber': insert_stmt.excluded.DraftNumber,
                'UpdatedAtSeason': insert_stmt.excluded.UpdatedAtSeason
            }
        )
        self.session.execute(stmt, players)
        self.session.commit()

    def update_players_table(self):
        print('updating players table...')
        last_season = self.get_last_season()
        handler = PlayersHandler(last_season)
        data = handler.downloader()
        data = data['resultSets'][0]['rowSet']
        data = [{
            'PlayerId': p[0],
            'FirstName': p[2],
            'LastName': p[1],
            'PlayerSlug': p[3],
            'Active': 1 if p[19] else 0,
            'Position': p[11],
            'Height': p[12],
            'Weigth': p[13],
            'College': p[14],
            'Country': p[15],
            'DraftYear': p[16],
            'DraftRound': p[17],
            'DraftNumber': p[18],
            'BirthDate': None,
            'UpdatedAtSeason': last_season
        } for p in data]
        self.insert_players(data)
