from typing import List, Dict, Any, Type
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Errors import InvalidActionCallError, IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionInput import ActionInput, SeasonRangeSelector, PlayersAutoComplete
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ResourceSpecifications.NBAAwardsResourceSpecification import NBAAwardsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.BREFSeasonsLinks import bref_seasons_links
from dbmanager.SharedData.PlayersIndex import players_index


class DownloadAllPlayersAwards(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return NBAAwardsResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_all_players_awards'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.nba_awards.actions.download_all_players_awards.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        return

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return []


class DownloadActivePlayersAwards(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return NBAAwardsResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_active_players_awards'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.nba_awards.actions.download_active_players_awards.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        return

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return []


class DownloadRookiesAwardsInSeasonsRange(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return NBAAwardsResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_rookies_awards_in_seasons_range'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.nba_awards.actions.download_rookies_awards_in_seasons_range.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        if params['start_season'] > params['end_season']:
            raise InvalidActionCallError(cls.get_resource().get_id(), cls.get_action_id(), params,
                                         'start season must be before end season')

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return [
            SeasonRangeSelector(bref_seasons_links.min_nba_season(),
                                bref_seasons_links.max_nba_season(),
                                bref_seasons_links.max_nba_season())
        ]


class DownloadPlayerAwards(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return NBAAwardsResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_player_awards'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.nba_awards.actions.download_player_awards.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        if not players_index.get_player_details(params['player_id']):
            raise IlegalParameterValueError(cls.get_action_id(), 'player_id', params['player_id'], 'cant find player with the supplied id')

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return [
            PlayersAutoComplete()
        ]
