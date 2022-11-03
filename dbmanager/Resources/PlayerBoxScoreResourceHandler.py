from typing import List, Type

from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.PlayerBoxScoreActions import UpdatePlayerBoxScoresAction, ResetPlayerBoxScoresAction, \
    UpdatePlayerBoxScoresInDateRangeAction, RedownloadPlayerBoxScoresInDateRangeAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.PlayerBoxScoreResourceSpecification import \
    PlayerBoxScoreResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.DataTypes.SeasonType import SEASON_TYPES


class PlayerBoxScoreResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return PlayerBoxScoreResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            UpdatePlayerBoxScoresAction,
            ResetPlayerBoxScoresAction,
            UpdatePlayerBoxScoresInDateRangeAction,
            RedownloadPlayerBoxScoresInDateRangeAction,
        ]

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
                StatusOption.INFO,
            )
            games_message = ResourceMessage(
                gettext('resources.playerboxscore.messages.games_message.title', season_type=season_type.name),
                gettext('resources.playerboxscore.messages.games_message.text', games_count=games_count),
                StatusOption.INFO,
            )
            to_ret.append(seasons_message)
            to_ret.append(games_message)
        return to_ret
