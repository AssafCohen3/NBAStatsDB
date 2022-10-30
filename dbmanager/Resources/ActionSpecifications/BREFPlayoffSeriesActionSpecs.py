from typing import List, Type
from dbmanager.AppI18n import gettext
from dbmanager.Errors import IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionInput import SeasonRangeSelector
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionInput
from dbmanager.Resources.ResourceSpecifications.BREFPlayoffSeriesResourceSpecification import \
    BREFPlayoffSeriesResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.BREFSeasonsLinks import bref_seasons_links


class UpdateBREFPlayoffSeries(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFPlayoffSeriesResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_bref_playoff_series'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_playoff_series.actions.update_bref_playoff_series.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return []


class RedownloadBREFPlayoffSeries(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFPlayoffSeriesResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'redownload_bref_playoff_series'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_playoff_series.actions.redownload_bref_playoff_series.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return []


class RedownloadBREFPlayoffSeriesInSeasonsRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFPlayoffSeriesResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
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
    def get_action_id(cls) -> str:
        return 'redownload_bref_playoff_series_in_season_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_playoff_series.actions.redownload_bref_playoff_series_in_season_range.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonRangeSelector(bref_seasons_links.min_nba_season(),
                                bref_seasons_links.max_nba_season(),
                                bref_seasons_links.max_nba_season())
        ]
