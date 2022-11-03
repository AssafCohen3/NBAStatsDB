import datetime
from typing import List, Type
from dbmanager.AppI18n import gettext
from dbmanager.Errors import IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionInput
from dbmanager.Resources.ActionSpecifications.ActionInput import SeasonTypeSelector, DateRangeSelector
from dbmanager.Resources.ResourceSpecifications.TeamBoxScoreResourceSpecification import \
    TeamBoxScoreResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.DataTypes.SeasonType import get_season_types
from dbmanager.constants import FIRST_NBA_SEASON


class UpdateTeamBoxScores(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return TeamBoxScoreResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_team_boxscores'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.teamboxscore.actions.update_team_boxscores.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector()
        ]


class ResetTeamBoxScores(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return TeamBoxScoreResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'reset_team_boxscores'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.teamboxscore.actions.reset_team_boxscores.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector()
        ]


class UpdateTeamBoxScoresInDateRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return TeamBoxScoreResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_team_boxscores_in_date_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.teamboxscore.actions.update_team_boxscores_in_date_range.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector(),
            # TODO maybe dont use constant
            DateRangeSelector(datetime.date(FIRST_NBA_SEASON, 1, 1),
                              datetime.date.today(),
                              datetime.date.today())
        ]


class RedownloadTeamBoxScoresInDateRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return TeamBoxScoreResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'redownload_team_boxscores_in_date_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.teamboxscore.actions.redownload_team_boxscores_in_date_range.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector(),
            # TODO maybe dont use constant
            DateRangeSelector(datetime.date(FIRST_NBA_SEASON, 1, 1),
                              datetime.date.today(),
                              datetime.date.today())
        ]
