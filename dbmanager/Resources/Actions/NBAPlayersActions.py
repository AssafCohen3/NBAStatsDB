from typing import Union, Type
from sqlalchemy.dialects.sqlite import insert

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAPlayer import NBAPlayer
from dbmanager.Downloaders.NBAPlayersDownloader import NBAPlayersDownloader
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.NBAPlayersActionSpecs import UpdateNBAPlayers
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SharedData.TodayConfig import today_config
from dbmanager.tasks.RetryManager import retry_wrapper


class UpdateNBAPlayersAction(ActionAbc):
    def init_task_data_abs(self) -> bool:
        return False

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdateNBAPlayers

    def insert_players(self, players):
        if not players:
            return
        insert_stmt = insert(NBAPlayer)
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
                'FirstSeason': insert_stmt.excluded.FirstSeason,
            }
        )
        self.session.execute(stmt, players)
        self.session.commit()
        self.update_resource()

    @retry_wrapper
    async def action(self):
        last_season = today_config.get_current_season()
        # TODO this may cause bugs because prod last season seems to refer to the year in which the season ended
        #  while the downloader expects for the year in which the season started. check this when season starts
        downloader = NBAPlayersDownloader(last_season)
        data = await downloader.download()
        data = data['resultSets'][0]['rowSet']
        data = [{
            'PlayerId': p[0],
            'FirstName': p[2],
            'LastName': p[1],
            'PlayerSlug': p[3],
            'Active': 1 if int(p[25]) >= last_season else 0,
            'Position': p[11],
            'Height': p[12],
            'Weight': int(p[13]) if p[13] else None,
            'College': p[14],
            'Country': p[15],
            'DraftYear': p[16],
            'DraftRound': p[17],
            'DraftNumber': p[18],
            'FirstSeason': int(p[24]),
            'BirthDate': None,
        } for p in data]
        self.insert_players(data)
        await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return 1

    def get_current_subtask_text_abs(self) -> str:
        return gettext('resources.nba_players.actions.update_nba_players.fetching_players')
