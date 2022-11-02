from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFTransaction import BREFTransaction
from dbmanager.Resources.ResourceSpecifications.BREFPlayersResourceSpecification import BREFPlayersResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, Source
from dbmanager.base import MyModel


class BREFTransactionsResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'bref_transactions'

    @classmethod
    def get_name(cls) -> str:
        return 'Transactions(BREF)'

    @classmethod
    def get_related_tables(cls) -> List[Type[MyModel]]:
        return [
            BREFTransaction
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return [
            BREFPlayersResourceSpecification
        ]

    @classmethod
    def get_source(cls) -> Source:
        return Source('BREF', 'https://www.basketball-reference.com/leagues/NBA_2023_transactions.html')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.bref_transactions.description')
