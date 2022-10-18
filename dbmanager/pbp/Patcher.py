# noinspection PyUnresolvedReferences
import dbmanager.pbp.PatchTimeout
from pbpstats.resources.enhanced_pbp.rebound import EventOrderError
from pbpstats.resources.enhanced_pbp.stats_nba import StatsViolation
from pbpstats import HEADERS, REQUEST_TIMEOUT
from pbpstats.resources.enhanced_pbp import (
    FieldGoal,
    Foul,
    FreeThrow,
    JumpBall,
    Substitution,
    Rebound,
    Timeout,
    Turnover, InvalidNumberOfStartersException,
)
from pbpstats.resources.enhanced_pbp.stats_nba.rebound import StatsRebound
import pbpstats.resources.enhanced_pbp.stats_nba.enhanced_pbp_item as pbpItemClass
from pbpstats.resources.enhanced_pbp.stats_nba.enhanced_pbp_item import StatsEnhancedPbpItem
from pbpstats.resources.enhanced_pbp.stats_nba.start_of_period import StatsStartOfPeriod

from dbmanager.RequestHandlers.StatsAsyncRequestHandler import stats_session

pbpItemClass.KEY_ATTR_MAPPER['WCTIMESTRING'] = 'real_time'
pbpItemClass.KEY_ATTR_MAPPER['PERSON1TYPE'] = 'person1_type'
pbpItemClass.KEY_ATTR_MAPPER['PERSON2TYPE'] = 'person2_type'
pbpItemClass.KEY_ATTR_MAPPER['PLAYER2_TEAM_ID'] = 'player2_team_id'
pbpItemClass.KEY_ATTR_MAPPER['PERSON3TYPE'] = 'person3_type'
pbpItemClass.KEY_ATTR_MAPPER['PLAYER3_TEAM_ID'] = 'player3_team_id'
pbpItemClass.KEY_ATTR_MAPPER['SCOREMARGIN'] = 'score_margin_text'


def _get_starters_from_boxscore_request(self):
    """
    makes request to boxscore url for time from period start to first event to get period starters
    """
    base_url = (
        f"https://stats.{self.league_url_part}.com/stats/boxscoretraditionalv2"
    )
    event = self
    while event is not None and event.seconds_remaining == self.seconds_remaining:
        event = event.next_event
    seconds_to_first_event = self.seconds_remaining - event.seconds_remaining

    if self.period == 1:
        start_range = 0
    elif self.period <= 4:
        start_range = int(7200 * (self.period - 1))
    else:
        start_range = int(28800 + 3000 * (self.period - 5))
    end_range = int(start_range + seconds_to_first_event * 10)
    params = {
        "GameId": self.game_id,
        "StartPeriod": 0,
        "EndPeriod": 0,
        "RangeType": 2,
        "StartRange": start_range + 1,
        "EndRange": end_range,
    }
    starters_by_team = {}
    response = stats_session.get(
        base_url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT
    )
    if response.status_code == 200:
        response_json = response.json()
        headers = response_json["resultSets"][0]["headers"]
        rows = response_json["resultSets"][0]["rowSet"]
        players = [dict(zip(headers, row)) for row in rows]
        starters = sorted(
            players, key=lambda k: int(k["MIN"].split(":")[1]), reverse=True
        )
        for starter in starters[0:10]:
            team_id = starter["TEAM_ID"]
            player_id = starter["PLAYER_ID"]
            if team_id not in starters_by_team.keys():
                starters_by_team[team_id] = []
            starters_by_team[team_id].append(player_id)
    else:
        response.raise_for_status()
    for team_id, starters in starters_by_team.items():
        if len(starters) != 5:
            raise InvalidNumberOfStartersException(
                f"GameId: {self.game_id}, Period: {self.period}, TeamId: {team_id}, Players: {starters}"
            )

    return starters_by_team


def get_offense_team_id(self):
    """
    returns team id for team on offense for event
    """
    if isinstance(self, Foul) and (self.is_charge or self.is_offensive_foul):
        # offensive foul returns team id
        # this isn't separate method in Foul class because some fouls can be committed
        # on offense or defense (loose ball, flagrant, technical)
        return getattr(self, 'team_id')
    event_to_check = self.previous_event
    team_ids = list(self.current_players.keys())
    while event_to_check is not None and not (
            isinstance(event_to_check, (FieldGoal, JumpBall))
            or (
                    isinstance(event_to_check, Turnover)
                    and not event_to_check.is_no_turnover
            )
            or (isinstance(event_to_check, Rebound) and event_to_check.is_real_rebound)
            or (
                    isinstance(event_to_check, FreeThrow)
                    and not event_to_check.is_technical_ft
            )
    ):
        event_to_check = getattr(event_to_check, 'previous_event')
    if event_to_check is None and self.next_event is not None \
            and (not isinstance(self.next_event, Turnover) or not self.next_event.is_no_turnover or self.next_event.previous_event != self):
        # should only get here on first possession of period when first event is non-offensive foul,
        # FieldGoal, FreeThrow, Rebound, Turnover, JumpBall
        return self.next_event.get_offense_team_id()
    if isinstance(event_to_check, Turnover) and not event_to_check.is_no_turnover:
        return (
            team_ids[0]
            if team_ids[1] == getattr(event_to_check, 'get_offense_team_id')()
            else team_ids[1]
        )
    if isinstance(event_to_check, Rebound) and event_to_check.is_real_rebound:
        if not event_to_check.oreb:
            return (
                team_ids[0]
                if team_ids[1] == getattr(event_to_check, 'get_offense_team_id')()
                else team_ids[1]
            )
        return getattr(event_to_check, 'get_offense_team_id')()
    if isinstance(event_to_check, (FieldGoal, FreeThrow)):
        if getattr(event_to_check, 'is_possession_ending_event'):
            return (
                team_ids[0]
                if team_ids[1] == getattr(event_to_check, 'get_offense_team_id')()
                else team_ids[1]
            )
        return getattr(event_to_check, 'get_offense_team_id')()
    if isinstance(event_to_check, JumpBall):
        if getattr(event_to_check, 'count_as_possession'):
            team_ids = list(self.current_players.keys())
            return (
                team_ids[0]
                if team_ids[1] == getattr(event_to_check, 'get_offense_team_id')()
                else team_ids[1]
            )
        return getattr(event_to_check, 'get_offense_team_id')()


# dummy object for the missed shot mock
class Object(object):
    pass


@property
def new_rebound_missed_shot_property(self):
    """
    returns :obj:`~pbpstats.resources.enhanced_pbp.field_goal.FieldGoal` or
    :obj:`~pbpstats.resources.enhanced_pbp.free_throw.FreeThrow` object
    for shot that was missed

    :raises: :obj:`~pbpstats.resources.enhanced_pbp.rebound.EventOrderError`:
        If rebound event is not immediately following a missed shot event.
    """
    if isinstance(self.previous_event, (FieldGoal, FreeThrow)):
        if not self.previous_event.is_made:
            return self.previous_event
    elif (
        isinstance(self.previous_event, Turnover)
        and self.previous_event.is_shot_clock_violation
    ):
        if isinstance(self.previous_event, FieldGoal):
            return getattr(self.previous_event, 'previous_event')
    elif isinstance(self.previous_event, JumpBall):
        prev_event = getattr(self.previous_event, 'previous_event')
        while isinstance(prev_event, (Substitution, Timeout)):
            prev_event = getattr(prev_event, 'previous_event')
        if isinstance(prev_event, (FieldGoal, FreeThrow)):
            return prev_event
    to_ret = Object()
    setattr(to_ret, 'seconds_remaining', 20)
    setattr(to_ret, 'team_id', None)
    return to_ret


@property
def missed_shot(self):
    """
    returns :obj:`~pbpstats.resources.enhanced_pbp.field_goal.FieldGoal` or
    :obj:`~pbpstats.resources.enhanced_pbp.free_throw.FreeThrow` object
    for shot that was missed

    :raises: :obj:`~pbpstats.resources.enhanced_pbp.rebound.EventOrderError`:
        If rebound event is not immediately following a missed shot event.
    """
    if isinstance(self.previous_event, (FieldGoal, FreeThrow)):
        if not self.previous_event.is_made:
            return self.previous_event
    elif (
        isinstance(self.previous_event, Turnover)
        and self.previous_event.is_shot_clock_violation
    ):
        if isinstance(self.previous_event, FieldGoal):
            return getattr(self.previous_event, 'previous_event')
    elif isinstance(self.previous_event, JumpBall):
        prev_event = getattr(self.previous_event, 'previous_event')
        while isinstance(prev_event, (Substitution, Timeout)):
            prev_event = getattr(prev_event, 'previous_event')
        if isinstance(prev_event, (FieldGoal, FreeThrow)):
            return prev_event
    elif isinstance(self.previous_event, StatsViolation) and self.previous_event.is_lane_violation \
            and isinstance(getattr(self.previous_event, 'previous_event'), (FieldGoal, FreeThrow)):
        if not getattr(self.previous_event, 'previous_event').is_made:
            return getattr(self.previous_event, 'previous_event')
    raise EventOrderError(
        f"previous event: {self.previous_event} is not a missed free throw or field goal"
    )


setattr(StatsRebound, 'missed_shot', new_rebound_missed_shot_property)
setattr(StatsEnhancedPbpItem, 'get_offense_team_id', get_offense_team_id)
setattr(StatsStartOfPeriod, '_get_starters_from_boxscore_request', _get_starters_from_boxscore_request)
