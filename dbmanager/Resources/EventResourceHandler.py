from json import dumps
from urllib.error import HTTPError
from alive_progress import alive_it
from sqlalchemy import and_, or_, outerjoin
from sqlalchemy.sql import select
from dbmanager.Database.Models.BoxScoreT import BoxScoreT
from dbmanager.Database.Models.Event import Event
from dbmanager.Handlers.PBPHandler import PBPHandler
from dbmanager.MainRequestsSession import call_with_retry, requests_session as requests
from dbmanager.Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert
from dbmanager.constants import SEASON_TYPES
from dbmanager.pbp.MyPBPLoader import MyPBPLoader


class EventResourceHandler(ResourceAbc):

    def __init__(self, session):
        self.count = 0
        super().__init__(session)

    @staticmethod
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

    @staticmethod
    def remove_empty_sub_events(events):
        to_filter = events['resultSets'][0]['rowSet']
        to_filter = [e for e in to_filter if not (
                e[2] == 8 and
                e[12] == 0 and
                e[19] == 0 and
                e[26] == 0
        )]
        events['resultSets'][0]['rowSet'] = to_filter

    @staticmethod
    def remove_unnecessery_overtimes(events):
        to_filter = events['resultSets'][0]['rowSet']
        if to_filter[-1][2] == 12 and to_filter[-1][4] > 4:
            to_filter.pop(len(to_filter) - 1)
        events['resultSets'][0]['rowSet'] = to_filter

    @staticmethod
    def remove_subtitutions_at_end(events):
        to_filter = events['resultSets'][0]['rowSet']
        if to_filter[-1][2] == 8:
            to_filter.pop(len(to_filter) - 1)
        events['resultSets'][0]['rowSet'] = to_filter

    def fix_events(self, events):
        self.fix_order_when_jumpball_before_start_of_perios(events)
        self.remove_unnecessery_overtimes(events)
        self.remove_empty_sub_events(events)
        self.remove_subtitutions_at_end(events)

    @staticmethod
    def add_possesion_number(events):
        current_possesion = 0
        sorted_events = sorted(events, key=lambda ev: ev.order)
        for e in sorted_events:
            setattr(e, 'possesion_number', current_possesion)
            if e.is_possession_ending_event:
                current_possesion += 1

    def transform_game_events(self, season, season_type, game_id, team_a_id, team_a_name, team_b_id, team_b_name, events):
        self.fix_events(events)
        tranformed_events = MyPBPLoader(game_id, events)
        self.add_possesion_number(tranformed_events.items)
        tranformed_events = [
            [
                season,
                season_type,
                e.game_id,
                team_a_id,
                team_a_name,
                team_b_id,
                team_b_name,
                e.event_num,
                e.event_type,
                e.event_action_type,
                e.period,
                e.real_time,
                e.clock,
                e.seconds_remaining,
                e.description,
                e.score[team_a_id],
                e.score[team_b_id],
                e.previous_event.score[team_a_id] - e.previous_event.score[team_b_id] if hasattr(e, 'shot_value') else
                e.score[team_a_id] - e.score[team_b_id],
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
                dumps([int(i) for i in e.lineup_ids[team_a_id].split('-')]),
                dumps([int(i) for i in e.lineup_ids[team_b_id].split('-')]),
                e.fouls_to_give[team_a_id],
                e.fouls_to_give[team_b_id],
                e.previous_event.event_num if e.previous_event else None,
                e.next_event.event_num if e.next_event else None,
                e.order,
                e.possesion_number
            ]
            for e in tranformed_events.items
        ]
        return tranformed_events

    # fetch all games without events
    def get_games_without_events(self, season_type_code):
        joined = outerjoin(BoxScoreT, Event, Event.GameId == BoxScoreT.GameId)
        stmt = (
            select(BoxScoreT.Season, BoxScoreT.SeasonType, BoxScoreT.GameDate, BoxScoreT.GameId, BoxScoreT.TeamAId, BoxScoreT.TeamAName, BoxScoreT.TeamBId, BoxScoreT.TeamBName)
            .select_from(joined)
            .where(and_(Event.GameId.is_(None),
                        BoxScoreT.SeasonType == season_type_code,
                        or_(
                            and_(BoxScoreT.SeasonType.in_([2, 4, 5]), BoxScoreT.Season >= 1996).self_group(),
                            and_(BoxScoreT.SeasonType == 3, or_(BoxScoreT.Season == 1997, BoxScoreT.Season >= 2003).self_group()).self_group()
                        ).self_group(),
                        ~BoxScoreT.WL.is_(None)
                        )
                   ).
            distinct()
        )
        return self.session.execute(stmt).fetchall()

    def insert_events(self, events):
        if not events:
            return
        stmt = insert(Event).on_conflict_do_nothing()
        self.session.execute(stmt, events)
        self.session.commit()

    # download and saves all events of a game
    def collect_all_game_events(self, season, season_type, game_id, teamaid, teamaname, teambid, teambname):
        handler = PBPHandler(game_id)
        data = call_with_retry(handler.downloader, 2)
        if not data:
            print(f'failed to fetch {game_id} events. try again later.')
            return
        self.count += 1
        try:
            transformed_events = self.transform_game_events(season, season_type, game_id, teamaid, teamaname, teambid, teambname, data)
        except HTTPError as e:
            print(f'failed transforming {game_id} events. try again later. error: {str(e)}')
            return
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
        self.insert_events(dicts)

    # updates all missing events of season type games
    def update_missing_events(self, season_type):
        print(f'updating missing events of {season_type["name"]}')
        games_missing_events = self.get_games_without_events(season_type["code"])
        if len(games_missing_events) == 0:
            return
        to_iterate = alive_it(games_missing_events, force_tty=True, title=f'Fetching {season_type["name"]} events', enrich_print=False, dual_line=True)
        for missing_game_season, missing_game_season_type, missing_game_date, gid, teamaid, teamaname, teambid, teambname in to_iterate:
            to_iterate.text(f'-> Fetching {teamaname} vs {teambname}, {missing_game_date} events...')
            self.collect_all_game_events(missing_game_season, missing_game_season_type, gid, teamaid, teamaname, teambid, teambname)
            # time.sleep(STATS_DELAY_SECONDS)  # sleep to prevent ban
            if self.count >= 550:
                print('clearing session...')
                requests.cookies.clear()
                self.count = 0

    # update all missing events
    def update_all_missing_events(self):
        for season_type in SEASON_TYPES:
            self.update_missing_events(season_type)
