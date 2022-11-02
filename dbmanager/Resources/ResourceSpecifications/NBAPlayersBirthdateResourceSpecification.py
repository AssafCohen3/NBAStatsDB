from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAPlayer import NBAPlayer
from dbmanager.Resources.ResourceSpecifications.NBAPlayersResourceSpecification import NBAPlayersResourceSpecification
from dbmanager.Resources.ResourceSpecifications.PlayerBoxScoreResourceSpecification import \
    PlayerBoxScoreResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, Source
from dbmanager.base import MyModel


class NBAPlayersBirthdateResourceSpecification(ResourceSpecificationAbc):

    @classmethod
    def get_id(cls) -> str:
        return 'nba_players_birthdate'

    @classmethod
    def get_name(cls) -> str:
        return 'Players Birthdate(NBA)'

    @classmethod
    def get_related_tables(cls) -> List[Type[MyModel]]:
        return [
            NBAPlayer
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return [
            PlayerBoxScoreResourceSpecification,
            NBAPlayersResourceSpecification
        ]

    @classmethod
    def get_source(cls) -> Source:
        return Source('stats.nba', 'https://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=2016&TeamID=1610612761')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.nba_players_birthdate.description')
