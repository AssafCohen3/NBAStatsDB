from typing import List, Type, Set, Optional
from sqlalchemy import select
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFPlayoffSerie import BREFPlayoffSerie
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.BREFPlayoffSeriesActions import UpdateBREFPlayoffSeriesAction, \
    RedownloadBREFPlayoffSeriesAction, RedownloadBREFPlayoffSeriesInSeasonsRangeAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.BREFPlayoffSeriesResourceSpecification import \
    BREFPlayoffSeriesResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.LeagueSchedule import playoff_schedule


class BREFPlayoffSeriesResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return BREFPlayoffSeriesResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            UpdateBREFPlayoffSeriesAction,
            RedownloadBREFPlayoffSeriesAction,
            RedownloadBREFPlayoffSeriesInSeasonsRangeAction
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        finished_matchups_stmt = (
            select(BREFPlayoffSerie.Season, BREFPlayoffSerie.TeamAId, BREFPlayoffSerie.TeamBId, BREFPlayoffSerie.SerieStartDate, BREFPlayoffSerie.SerieEndDate)
        )
        finished_matchups = session.execute(finished_matchups_stmt).fetchall()
        exist_seasons: Set[int] = set()
        possible_seasons: Set[int] = set()
        not_updated_seasons: Set[int] = set()
        min_season: Optional[int] = None
        max_season: Optional[int] = None
        matchups_dict = {}
        for season, team_a_id, team_b_id, start_date, end_date in finished_matchups:
            exist_seasons.add(season)
            matchups_dict[(season, team_a_id, team_b_id)] = (start_date, end_date)
            min_season = min(season, min_season) if min_season else season
            max_season = max(season, max_season) if max_season else season
        possible_matchups = playoff_schedule.get_matchups()
        for possible_matchup in possible_matchups:
            possible_seasons.add(possible_matchup.season)
            saved_res = matchups_dict.get((possible_matchup.season, possible_matchup.team_a_id, possible_matchup.team_b_id))
            if (saved_res is None or
                    saved_res[0].isoformat() != possible_matchup.start_date or
                    saved_res[1].isoformat() != possible_matchup.end_date):
                not_updated_seasons.add(possible_matchup.season)
        existing_seasons_count = len(exist_seasons)
        possible_seasons_count = len(possible_seasons)
        completed_seasons_count = possible_seasons_count - len(not_updated_seasons)
        existing_series_count = len(finished_matchups)
        possible_matchups_count = len(possible_matchups)
        return [
            # Seasons with playoff sereis:
            # 13 out of 76 Seasons
            ResourceMessage(
                gettext('resources.bref_playoff_series.messages.collected_seasons.title'),
                gettext('resources.bref_playoff_series.messages.collected_seasons.text', seasons_count=existing_seasons_count, possible_seasons_count=possible_seasons_count),
                StatusOption.OK if existing_seasons_count == possible_seasons_count else StatusOption.MISSING,
            ),
            # Seasons with full playoff series:
            # 14 out of 76 Seasons
            ResourceMessage(
                gettext('resources.bref_playoff_series.messages.collected_full_seasons.title'),
                gettext('resources.bref_playoff_series.messages.collected_full_seasons.text',
                        seasons_count=completed_seasons_count, possible_seasons_count=possible_seasons_count),
                StatusOption.OK if completed_seasons_count == possible_seasons_count else StatusOption.MISSING,
            ),
            # Series Count:
            # 444 sereis out of 6777 possible series
            ResourceMessage(
                gettext('resources.bref_playoff_series.messages.collected_series.title'),
                gettext('resources.bref_playoff_series.messages.collected_series.text',
                        series_count=existing_series_count, possible_series_count=possible_matchups_count),
                StatusOption.OK if existing_series_count == possible_matchups_count else StatusOption.MISSING,
            ),
            # First Season with playoff serie:
            # 1956
            ResourceMessage(
                gettext('resources.bref_playoff_series.messages.first_season.title'),
                gettext('resources.bref_playoff_series.messages.first_season.text',
                        season=min_season if min_season else gettext('common.none')),
                StatusOption.INFO
            ),
            # Last Season with playoff serie
            ResourceMessage(
                gettext('resources.bref_playoff_series.messages.last_season.title'),
                gettext('resources.bref_playoff_series.messages.last_season.text',
                        season=max_season if max_season else gettext('common.none')),
                StatusOption.INFO
            ),
        ]
