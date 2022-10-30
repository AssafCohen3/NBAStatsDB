from typing import List, Type
from dbmanager.AppI18n import gettext
from dbmanager.Errors import IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionInput import SeasonRangeSelector
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionInput
from dbmanager.Resources.ResourceSpecifications.OddsResourceSpecification import OddsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.SeasonPlayoffs import get_last_season_with_playoffs
from dbmanager.constants import FIRST_ODDS_SEASON, EXCLUDED_ODDS_SEASONS


class UpdateOdds(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return OddsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_odds'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.odds.actions.update_odds.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return []


class RedownloadOdds(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return OddsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'redownload_odds'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.odds.actions.redownload_odds.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return []


class RedownloadOddsInSeasonsRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return OddsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        min_season = FIRST_ODDS_SEASON
        max_season = get_last_season_with_playoffs()
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
    def get_action_id(cls) -> str:
        return 'redownload_odds_in_season_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.odds.actions.redownload_odds_in_season_range.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonRangeSelector(FIRST_ODDS_SEASON,
                                get_last_season_with_playoffs(),
                                get_last_season_with_playoffs(),
                                EXCLUDED_ODDS_SEASONS)
        ]
