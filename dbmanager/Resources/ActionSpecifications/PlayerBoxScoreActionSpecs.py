import datetime
from typing import List, Type
from dbmanager.AppI18n import gettext
from dbmanager.Errors import IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionInput
from dbmanager.Resources.ActionSpecifications.ActionInput import SeasonTypeSelector, DateRangeSelector
from dbmanager.Resources.ResourceSpecifications.PlayerBoxScoreResourceSpecification import \
    PlayerBoxScoreResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SeasonType import get_season_types
from dbmanager.constants import FIRST_NBA_SEASON


class UpdatePlayerBoxScores(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return PlayerBoxScoreResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_player_boxscores'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.playerboxscore.actions.update_player_boxscores.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector()
        ]


class ResetPlayerBoxScores(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return PlayerBoxScoreResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'reset_player_boxscores'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.playerboxscore.actions.reset_player_boxscores.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector()
        ]


class UpdatePlayerBoxScoresInDateRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return PlayerBoxScoreResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        type_code = params['season_type_code']
        season_types = get_season_types(type_code)
        if len(season_types) == 0:
            raise IlegalParameterValueError(cls, 'season_type_code',
                                            params['season_type_code'], 'Season type code not exist')

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_player_boxscores_in_date_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.playerboxscore.actions.update_player_boxscores_in_date_range.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            SeasonTypeSelector(),
            # TODO maybe dont use constant
            DateRangeSelector(datetime.date(FIRST_NBA_SEASON, 1, 1),
                              datetime.date.today(),
                              datetime.date.today())
        ]
