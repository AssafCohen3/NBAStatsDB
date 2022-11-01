import datetime
from typing import List, Type, Dict, Any
from dbmanager.AppI18n import gettext
from dbmanager.Errors import IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionInput, \
    ActionDependency
from dbmanager.Resources.ActionSpecifications.ActionInput import SeasonTypeSelector, DateRangeSelector
from dbmanager.Resources.ActionSpecifications.TeamBoxScoreActionSpecs import UpdateTeamBoxScores, \
    UpdateTeamBoxScoresInDateRange
from dbmanager.Resources.ResourceSpecifications.EventsResourceSpecification import EventsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SeasonType import get_season_types
from dbmanager.constants import FIRST_NBA_SEASON


class UpdateEvents(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return EventsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_events'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.events.actions.update_events.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector()
        ]

    @classmethod
    def get_action_dependencies(cls, parsed_params: Dict[str, Any]) -> List[ActionDependency]:
        return [
            ActionDependency(UpdateTeamBoxScores, parsed_params)
        ]


class ResetEvents(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return EventsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'reset_events'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.events.actions.reset_events.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector()
        ]

    @classmethod
    def get_action_dependencies(cls, parsed_params: Dict[str, Any]) -> List[ActionDependency]:
        return [
            ActionDependency(UpdateTeamBoxScores, parsed_params)
        ]


class UpdateEventsInDateRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return EventsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_events_in_date_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.events.actions.update_events_in_date_range.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector(),
            # TODO maybe dont use constant
            DateRangeSelector(datetime.date(FIRST_NBA_SEASON, 1, 1),
                              datetime.date.today(),
                              datetime.date.today())
        ]

    @classmethod
    def get_action_dependencies(cls, parsed_params: Dict[str, Any]) -> List[ActionDependency]:
        return [
            ActionDependency(UpdateTeamBoxScoresInDateRange, parsed_params)
        ]


class ResetEventsInDateRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return EventsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'reset_events_in_date_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.events.actions.reset_events_in_date_range.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector(),
            # TODO maybe dont use constant
            DateRangeSelector(datetime.date(FIRST_NBA_SEASON, 1, 1),
                              datetime.date.today(),
                              datetime.date.today())
        ]

    @classmethod
    def get_action_dependencies(cls, parsed_params: Dict[str, Any]) -> List[ActionDependency]:
        return [
            ActionDependency(UpdateTeamBoxScoresInDateRange, parsed_params)
        ]
