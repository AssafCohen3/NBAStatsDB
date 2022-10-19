from typing import List, Type
from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.Odds import Odds
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.OddsActions import UpdateOddsAction, RedownloadOddsAction, \
    RedownloadOddsInSeasonsRangeAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage
from dbmanager.Resources.ResourceSpecifications.OddsResourceSpecification import OddsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.BREFSeasonsLinks import bref_seasons_links
from dbmanager.SharedData.SeasonPlayoffs import get_last_season_with_playoffs, last_season_playoffs
from dbmanager.constants import FIRST_ODDS_SEASON, EXCLUDED_ODDS_SEASONS


class OddsResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return OddsResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            UpdateOddsAction,
            RedownloadOddsAction,
            RedownloadOddsInSeasonsRangeAction,
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        initial_list = [i for i in range(FIRST_ODDS_SEASON, get_last_season_with_playoffs() + 1) if i not in EXCLUDED_ODDS_SEASONS]
        seasons_count = len(initial_list)
        missing_seasons = []
        last_rounds_stmt = (
            select(Odds.Season, func.min(Odds.Round)).
            group_by(Odds.Season)
        )
        last_rounds = session.execute(last_rounds_stmt).fetchall()
        last_rounds = {season: last_round for season, last_round in last_rounds}
        last_season = bref_seasons_links.max_nba_season()
        for season in initial_list:
            if (season not in last_rounds or
                    # dubious condition. this assumes that if you downloaded the data of old seasons once its enough
                    # so only new seasons may be partially downloaded
                    (last_season > season >= 2020 and last_rounds[season] > 1) or
                    (season == last_season and last_rounds[season] > last_season_playoffs.get_last_round())):
                missing_seasons.append(season)
        missing_seasons_count = len(missing_seasons)
        return [
            ResourceMessage(
                gettext('resources.odds.messages.seasons_with_odds.title'),
                gettext('resources.odds.messages.seasons_with_odds.text',
                        seasons_count=seasons_count,
                        odds_seasons_count=seasons_count - missing_seasons_count),
                'ok' if missing_seasons_count == 0 else 'missing'
            )
        ]
