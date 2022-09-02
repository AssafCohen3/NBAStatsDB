from typing import List, Type

from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.PlayerBoxScoreActions import UpdatePlayerBoxScoresAction, ResetPlayerBoxScoresAction, \
    UpdatePlayerBoxScoresInDateRangeAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, RelatedTable, ResourceMessage
from dbmanager.SeasonType import SEASON_TYPES


class PlayerBoxScoreResourceHandler(ResourceAbc):

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            UpdatePlayerBoxScoresAction,
            ResetPlayerBoxScoresAction,
            UpdatePlayerBoxScoresInDateRangeAction
        ]

    @classmethod
    def get_id(cls) -> str:
        return 'playerboxscore'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'PlayerBoxScore'

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        to_ret = []
        stmt = (
            select(BoxScoreP.SeasonType, func.count(BoxScoreP.Season.distinct()), func.count(BoxScoreP.GameId.distinct())).
            group_by(BoxScoreP.SeasonType)
        )
        results = session.execute(stmt).fetchall()
        for season_type in SEASON_TYPES:
            res = [r for r in results if r[0] == season_type.code]
            seasons_count, games_count = res[0][1:] if len(res) > 0 else (0, 0)
            seasons_message = ResourceMessage(
                gettext('resources.playerboxscore.messages.seasons_message.title', season_type=season_type.name),
                gettext('resources.playerboxscore.messages.seasons_message.text', seasons_count=seasons_count),
                'ok'
            )
            games_message = ResourceMessage(
                gettext('resources.playerboxscore.messages.games_message.title', season_type=season_type.name),
                gettext('resources.playerboxscore.messages.games_message.text', games_count=games_count),
                'ok'
            )
            to_ret.append(seasons_message)
            to_ret.append(games_message)
        return to_ret

    @classmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        return [
            RelatedTable('BoxScoreP')
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceAbc']]:
        return []
