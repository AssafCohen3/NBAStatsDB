from typing import List, Dict, Any, Type

from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Errors import IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionInput import ActionInput, SeasonRangeSelector
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionDependency
from dbmanager.Resources.ResourceSpecifications.BREFCoachesResourceSpecification import BREFCoachesResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.BREFSeasonsLinks import bref_seasons_links


class DownloadAllCoaches(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFCoachesResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_coaches'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_coaches.actions.download_coaches.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        return

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return []

    @classmethod
    def get_action_dependencies(cls, parsed_params: Dict[str, Any]) -> List[ActionDependency]:
        return []


class DownloadCoachesInSeasonsRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFCoachesResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_coaches_in_seasons_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_coaches.actions.download_coaches_in_seasons_range.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        min_season = bref_seasons_links.min_nba_season()
        max_season = bref_seasons_links.max_nba_season()
        if params['start_season'] < min_season or params['start_season'] > max_season:
            raise IlegalParameterValueError(cls, 'start_season',
                                            params['start_season'], f'start_season must be between {min_season} and {max_season}')
        if params['end_season'] < min_season or params['end_season'] > max_season:
            raise IlegalParameterValueError(cls, 'end_season',
                                            params['end_season'], f'end_season must be between {min_season} and {max_season}')
        if params['end_season'] < params['start_season']:
            raise IlegalParameterValueError(cls, 'end_season',
                                            params['end_season'], f'end_season must be after {params["start_season"]}')

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return [
            SeasonRangeSelector(bref_seasons_links.min_nba_season(),
                                bref_seasons_links.max_nba_season(),
                                bref_seasons_links.max_nba_season())
        ]

    @classmethod
    def get_action_dependencies(cls, parsed_params: Dict[str, Any]) -> List[ActionDependency]:
        return []
