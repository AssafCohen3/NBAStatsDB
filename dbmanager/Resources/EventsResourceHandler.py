from typing import List, Type

from sqlalchemy import select, func, outerjoin, and_, or_
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreT import BoxScoreT
from dbmanager.Database.Models.Event import Event
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.EventsActions import UpdateEventsAction, ResetEventsAction, \
    UpdateEventsInDateRangeAction, ResetEventsInDateRangeAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage
from dbmanager.Resources.ResourceSpecifications.EventsResourceSpecification import EventsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SeasonType import SEASON_TYPES


class EventsResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return EventsResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            UpdateEventsAction,
            ResetEventsAction,
            UpdateEventsInDateRangeAction,
            ResetEventsInDateRangeAction,
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        joined = outerjoin(BoxScoreT, Event, Event.GameId == BoxScoreT.GameId)
        stmt = (
            select(BoxScoreT.SeasonType,
                   func.count(BoxScoreT.GameId.distinct()),
                   func.count(BoxScoreT.GameId).filter(Event.GameId.is_(None)))
            .select_from(joined)
            .where(and_(
                        or_(
                            and_(BoxScoreT.SeasonType.in_([2, 4, 5]), BoxScoreT.Season >= 1996).self_group(),
                            and_(BoxScoreT.SeasonType == 3, or_(BoxScoreT.Season == 1997, BoxScoreT.Season >= 2003).self_group()).self_group()
                        ).self_group(),
                        BoxScoreT.WL == 'W',
                        )
                   )
            .group_by(BoxScoreT.SeasonType)
        )
        data = session.execute(stmt).fetchall()
        to_ret = []
        for season_type in SEASON_TYPES:
            res = [r for r in data if r[0] == season_type.code]
            games_count, games_with_events = res[0][1:] if len(res) > 0 else (0, 0)
            games_message = ResourceMessage(
                gettext('resources.events.messages.games_message.title', season_type=season_type.name),
                gettext('resources.events.messages.games_message.text', games_count=games_count, games_with_events=games_count - games_with_events),
                'ok'
            )
            to_ret.append(games_message)
        return to_ret
