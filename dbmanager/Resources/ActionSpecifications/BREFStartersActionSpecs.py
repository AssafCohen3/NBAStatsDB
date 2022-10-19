from typing import List, Dict, Any, Type, Tuple, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Errors import InvalidActionCallError, IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionInput import ActionInput, SeasonRangeSelector
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ResourceSpecifications.BREFStartersResourceSpecification import \
    BREFStartersResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.constants import BREF_STARTERS_FIRST_SEASON


def get_starters_range(session: scoped_session) -> Tuple[Optional[int], Optional[int], int]:
    range_stmt = (
        select(func.min(BoxScoreP.Season), func.max(BoxScoreP.Season), func.count(BoxScoreP.GameId)).
        where(BoxScoreP.Season >= BREF_STARTERS_FIRST_SEASON)
    )
    min_season, max_season, count = session.execute(range_stmt).fetchall()[0]
    return min_season, max_season, count


class UpdateStarters(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFStartersResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_starters'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_starters.actions.update_starters.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        return

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return []


class RedownloadStarters(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFStartersResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'redownload_starters'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_starters.actions.redownload_starters.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        return

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return []


class RedownloadStartersInSeasonsRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFStartersResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'redownload_starters_in_seasons_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_starters.actions.redownload_starters_in_seasons_range.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        min_season, max_season, count = get_starters_range(session)
        if count == 0:
            raise InvalidActionCallError(cls, params, 'there is no boxscores in a season in which starters data exist')
        if params['start_season'] < min_season or params['start_season'] > max_season:
            raise IlegalParameterValueError(cls.get_action_id(), 'start_season',
                                            params['start_season'], f'start_season must be between {min_season} and {max_season}')
        if params['end_season'] < min_season or params['end_season'] > max_season:
            raise IlegalParameterValueError(cls.get_action_id(), 'end_season',
                                            params['end_season'], f'end_season must be between {min_season} and {max_season}')
        if params['end_season'] < params['start_season']:
            raise IlegalParameterValueError(cls.get_action_id(), 'end_season',
                                            params['end_season'], f'end_season must be after {params["start_season"]}')

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        min_season, max_season, count = get_starters_range(session)
        return [
            SeasonRangeSelector(
                min_season,
                max_season,
                max_season
            )
        ]
