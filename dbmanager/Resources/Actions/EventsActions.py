import datetime
from abc import ABC
from dataclasses import dataclass
from json import dumps
from typing import Union, Optional, List, Type
from sqlalchemy import select, delete, outerjoin, and_, or_
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreT import BoxScoreT
from dbmanager.Database.Models.Event import Event
from dbmanager.Downloaders.EventsDownloader import EventsDownloader
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.EventsActionSpecs import UpdateEvents, ResetEvents, \
    UpdateEventsInDateRange, ResetEventsInDateRange
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SeasonType import get_season_types, SeasonType
from dbmanager.pbp.MyPBPLoader import MyPBPLoader
from dbmanager.utils import iterate_with_next
from dbmanager.tasks.RetryManager import retry_wrapper


@dataclass
class GameDetails:
    season_type: SeasonType
    season: int
    game_id: str
    game_date: datetime.date
    team_a_id: int
    team_a_name: str
    team_b_id: int
    team_b_name: str


def fix_order_when_jumpball_before_start_of_perios(events):
    events = events['resultSets'][0]['rowSet']
    if events[0][2] != 12 and events[0][2] in (10, 7):
        if events[1][2] == 12:
            # jump ball and period start switched
            tmp_jump_ball = events[0]
            events[0] = events[1]
            events[1] = tmp_jump_ball
        else:
            replacement = [events[0][0], 0, 12, 0, 1, events[0][5], "12:00", None,
                           f"Start of 1st Period ({events[0][5]} EST)", None, None, None, 0, 0, None, None, None,
                           None, None, 0, 0, None, None, None, None, None, 0, 0, None, None, None, None, None, 0]
            events.insert(0, replacement)
            if events[1][1] <= 0:
                for e in events[1:]:
                    e[1] = e[1] + 1


def remove_empty_sub_events(events):
    to_filter = events['resultSets'][0]['rowSet']
    to_filter = [e for e in to_filter if not (
            e[2] == 8 and
            e[12] == 0 and
            e[19] == 0 and
            e[26] == 0
    )]
    events['resultSets'][0]['rowSet'] = to_filter


def remove_unnecessery_overtimes(events):
    to_filter = events['resultSets'][0]['rowSet']
    if to_filter[-1][2] == 12 and to_filter[-1][4] > 4:
        to_filter.pop(len(to_filter) - 1)
    events['resultSets'][0]['rowSet'] = to_filter


def remove_subtitutions_at_end(events):
    to_filter = events['resultSets'][0]['rowSet']
    if to_filter[-1][2] == 8:
        to_filter.pop(len(to_filter) - 1)
    events['resultSets'][0]['rowSet'] = to_filter


def fix_events(events):
    fix_order_when_jumpball_before_start_of_perios(events)
    remove_unnecessery_overtimes(events)
    remove_empty_sub_events(events)
    remove_subtitutions_at_end(events)


def add_possesion_number(events):
    current_possesion = 0
    sorted_events = sorted(events, key=lambda ev: ev.order)
    for e in sorted_events:
        setattr(e, 'possesion_number', current_possesion)
        if e.is_possession_ending_event:
            current_possesion += 1


async def transform_game_events(game_details: GameDetails, events: List[dict]):
    fix_events(events)
    pbp_loader = MyPBPLoader(game_details.game_id, events)
    await pbp_loader.my_make_pbp_items()
    add_possesion_number(pbp_loader.items)
    tranformed_events = [
        [
            game_details.season,
            game_details.season_type.code,
            e.game_id,
            game_details.team_a_id,
            game_details.team_a_name,
            game_details.team_b_id,
            game_details.team_b_name,
            e.event_num,
            e.event_type,
            e.event_action_type,
            e.period,
            e.real_time,
            e.clock,
            e.seconds_remaining,
            e.description,
            e.score[game_details.team_a_id],
            e.score[game_details.team_b_id],
            e.previous_event.score[game_details.team_a_id] - e.previous_event.score[game_details.team_b_id] if hasattr(e, 'shot_value') else
            e.score[game_details.team_a_id] - e.score[game_details.team_b_id],
            float(getattr(e, 'shot_value', 0)),
            getattr(e, 'person1_type', None),
            getattr(e, 'player1_id', None),
            getattr(e, 'team_id', None),
            getattr(e, 'person2_type', None),
            getattr(e, 'player2_id', None),
            getattr(e, 'player2_team_id', None),
            getattr(e, 'person3_type', None),
            getattr(e, 'player3_id', None),
            getattr(e, 'player3_team_id', None),
            1 if e.video_available else 0,
            1 if e.count_as_possession else 0,
            1 if e.is_possession_ending_event else 0,
            e.seconds_since_previous_event,
            dumps([int(i) for i in e.lineup_ids[game_details.team_a_id].split('-')]),
            dumps([int(i) for i in e.lineup_ids[game_details.team_b_id].split('-')]),
            e.fouls_to_give[game_details.team_a_id],
            e.fouls_to_give[game_details.team_b_id],
            e.previous_event.event_num if e.previous_event else None,
            e.next_event.event_num if e.next_event else None,
            e.order,
            e.possesion_number
        ]
        for e in pbp_loader.items
    ]
    return tranformed_events


class GeneralEventsAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session,
                 season_type_code: str,
                 start_date: datetime.date = None,
                 end_date: datetime.date = None,
                 update: bool = False):
        super().__init__(session)
        self.start_date: Optional[datetime.date] = start_date
        self.end_date: Optional[datetime.date] = end_date
        self.season_types: List[SeasonType] = get_season_types(season_type_code)
        self.update: bool = update
        self.games_to_fetch: List[GameDetails] = []
        self.current_game: Optional[GameDetails] = None

    def init_task_data_abs(self) -> bool:
        for season_type in self.season_types:
            games_to_add = self.get_games_without_events(season_type) if self.update else self.get_all_games(season_type)
            self.games_to_fetch.extend(games_to_add)
        self.current_game = self.games_to_fetch[0] if self.games_to_fetch else None
        return len(self.games_to_fetch) > 0

    def insert_events(self, game_id: str, events: List[dict]):
        delete_stmt = delete(Event).where(Event.GameId == game_id)
        self.session.execute(delete_stmt)
        if events:
            stmt = insert(Event).on_conflict_do_nothing()
            self.session.execute(stmt, events)
        self.session.commit()
        self.update_resource()

    @retry_wrapper
    async def collect_all_game_events(self, game_details: GameDetails):
        downloader = EventsDownloader(game_details.game_id)
        data = await downloader.download()
        transformed_events = await transform_game_events(game_details, data)
        headers = [
            'Season',
            'SeasonType',
            'GameId',
            'TeamAId',
            'TeamAName',
            'TeamBId',
            'TeamBName',
            'EventNumber',
            'EventType',
            'EventActionType',
            'Period',
            'RealTime',
            'Clock',
            'RemainingSeconds',
            'Description',
            'TeamAScore',
            'TeamBScore',
            'ScoreMargin',
            'ShotValue',
            'PersonAType',
            'PlayerAId',
            'PlayerATeamId',
            'PersonBType',
            'PlayerBId',
            'PlayerBTeamId',
            'PersonCType',
            'PlayerCId',
            'PlayerCTeamId',
            'VideoAvailable',
            'CountAsPossession',
            'IsPossessionEndingEvent',
            'SecondsSincePreviousEvent',
            'TeamALineupIds',
            'TeamBLineupIds',
            'TeamAFoulsToGive',
            'TeamBFoulsToGive',
            'PreviousEventNumber',
            'NextEventNumber',
            'EventOrder',
            'RealPossesionNumber'
        ]
        dicts = [dict(zip(headers, event)) for event in transformed_events]
        self.insert_events(game_details.game_id, dicts)

    def get_games_without_events(self, season_type: SeasonType):
        joined = outerjoin(BoxScoreT, Event, Event.GameId == BoxScoreT.GameId)
        stmt = (
            select(BoxScoreT.Season, BoxScoreT.GameId, BoxScoreT.GameDate,
                   BoxScoreT.TeamAId, BoxScoreT.TeamAName, BoxScoreT.TeamBId, BoxScoreT.TeamBName)
            .select_from(joined)
            .where(and_(Event.GameId.is_(None),
                        BoxScoreT.SeasonType == season_type.code,
                        or_(
                            and_(BoxScoreT.SeasonType.in_([2, 4, 5]), BoxScoreT.Season >= 1996).self_group(),
                            and_(BoxScoreT.SeasonType == 3, or_(BoxScoreT.Season == 1997, BoxScoreT.Season >= 2003).self_group()).self_group()
                        ).self_group(),
                        BoxScoreT.WL == 'W',
                        self.start_date is None or self.start_date <= BoxScoreT.GameDate,
                        self.end_date is None or self.end_date >= BoxScoreT.GameDate
                        )
                   )
        )
        to_ret = self.session.execute(stmt).fetchall()
        return [GameDetails(season_type, *g) for g in to_ret]

    def get_all_games(self, season_type: SeasonType):
        stmt = (
            select(BoxScoreT.Season, BoxScoreT.GameId, BoxScoreT.GameDate,
                   BoxScoreT.TeamAId, BoxScoreT.TeamAName, BoxScoreT.TeamBId, BoxScoreT.TeamBName)
            .where(and_(BoxScoreT.SeasonType == season_type.code,
                        or_(
                            and_(BoxScoreT.SeasonType.in_([2, 4, 5]), BoxScoreT.Season >= 1996).self_group(),
                            and_(BoxScoreT.SeasonType == 3, or_(BoxScoreT.Season == 1997, BoxScoreT.Season >= 2003).self_group()).self_group()
                        ).self_group(),
                        BoxScoreT.WL == 'W',
                        self.start_date is None or self.start_date <= BoxScoreT.GameDate,
                        self.end_date is None or self.end_date >= BoxScoreT.GameDate
                        )
                   )
        )
        to_ret = self.session.execute(stmt).fetchall()
        return [GameDetails(season_type, *g) for g in to_ret]

    async def action(self):
        for game, next_game in iterate_with_next(self.games_to_fetch):
            await self.collect_all_game_events(game)
            self.current_game = next_game
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.games_to_fetch)

    def get_current_subtask_text_abs(self) -> str:
        # Downloading events of {team a} vs {team b} ({date})
        return gettext('resources.events.actions.download_events.downloading_events',
                       team_a=self.current_game.team_a_name if self.current_game else '',
                       team_b=self.current_game.team_b_name if self.current_game else '',
                       game_date=self.current_game.game_date.isoformat() if self.current_game else '')


class UpdateEventsAction(GeneralEventsAction):

    def __init__(self, session: scoped_session, season_type_code: str):
        super().__init__(session, season_type_code, None, None, True)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdateEvents


class ResetEventsAction(GeneralEventsAction):

    def __init__(self, session: scoped_session, season_type_code: str):
        super().__init__(session, season_type_code, None, None, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return ResetEvents


class UpdateEventsInDateRangeAction(GeneralEventsAction):

    def __init__(self, session: scoped_session, season_type_code: str,
                 start_date: datetime.date = None, end_date: datetime.date = None):
        super().__init__(session, season_type_code, start_date, end_date, True)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdateEventsInDateRange


class ResetEventsInDateRangeAction(GeneralEventsAction):

    def __init__(self, session: scoped_session, season_type_code: str,
                 start_date: datetime.date = None, end_date: datetime.date = None):
        super().__init__(session, season_type_code, start_date, end_date, False)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return ResetEventsInDateRange
