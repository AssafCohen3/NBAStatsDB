from typing import List, Type
from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFTransaction import BREFTransaction
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.BREFTransactionsActions import DownloadAllTransactionsAction, \
    DownloadTransactionsInSeasonsRangeAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage
from dbmanager.Resources.ResourceSpecifications.BREFTransactionsResourceSpecification import \
    BREFTransactionsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class BREFTransactionsResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return BREFTransactionsResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            DownloadAllTransactionsAction,
            DownloadTransactionsInSeasonsRangeAction
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        transaction_key = (
                              BREFTransaction.Season.concat('-')
                              .concat(BREFTransaction.Month).concat('-')
                              .concat(BREFTransaction.Day).concat('-')
                              .concat(BREFTransaction.TransactionNumber)
        )
        stmt = (
            select(func.count(transaction_key.distinct()), func.count(BREFTransaction.Season.distinct()))
        )
        transactions_count, seasons_count = session.execute(stmt).fetchall()[0]
        return [
            ResourceMessage(
                gettext('resources.bref_transactions.messages.transactions_count.title'),
                gettext('resources.bref_transactions.messages.transactions_count.text',
                        transactions=transactions_count),
                'ok'
            ),
            ResourceMessage(
                gettext('resources.bref_transactions.messages.transactions_seasons_count.title'),
                gettext('resources.bref_transactions.messages.transactions_seasons_count.text',
                        seasons=seasons_count),
                'ok'
            ),
        ]
