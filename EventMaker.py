#  using https://github.com/dblackrun/pbpstats
from pbp.MyPBPLoader import MyPBPLoader


def fix_order_when_jumpball_before_start_of_perios(events):
    events = events['resultSets'][0]['rowSet']
    if events[0][2] != 12 and events[0][2] == 10:
        if events[1][2] == 12:
            # jump ball and period start switched
            tmp_jump_ball = events[0]
            events[0] = events[1]
            events[1] = tmp_jump_ball
        else:
            replacement = [events[0][0], 0, 12, 0, 1, events[0][5], "12:00", None, f"Start of 1st Period ({events[0][5]} EST)", None, None, None, 0, 0, None, None, None, None, None, 0, 0, None, None, None, None, None, 0, 0, None, None, None, None, None, 0]
            events.insert(0, replacement)
            if events[1][1] <= 0:
                for e in events[1:]:
                    e[1] = e[1] + 1


def inject_period_start_at_need(events):
    events = events['resultSets'][0]['rowSet']
    if events[0][2] == 12 and events[1][2] != 12:
        # jump ball and period start switched
        tmp_jump_ball = events[0]
        events[0] = events[1]
        events[1] = tmp_jump_ball


def transform_game_events(game_id, team_a_id, team_b_id, events):
    fix_order_when_jumpball_before_start_of_perios(events)
    tranformed_events = MyPBPLoader(game_id, events)
    tranformed_events = [
        [
            e.game_id,
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
            0 if getattr(e, 'score_margin_text', None) is None or e.score_margin_text == 'TIE' else int(e.score_margin_text),
            getattr(e, 'shot_value', None),
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
            e.lineup_ids[team_a_id],
            e.lineup_ids[team_b_id],
            e.fouls_to_give[team_a_id],
            e.fouls_to_give[team_b_id],
            e.previous_event.event_num if e.previous_event else None,
            e.next_event.event_num if e.next_event else None,
            e.order
        ]
        for e in tranformed_events.items
    ]
    return tranformed_events
