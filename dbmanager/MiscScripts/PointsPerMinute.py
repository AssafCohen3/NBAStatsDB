import sqlite3

import heapdict
from heapdict import heapdict

from dbmanager.constants import *


def main():
    conn = sqlite3.connect(DATABASE_PATH + DATABASE_NAME + '.sqlite')
    query = """
    with
    MinutedGames as(
    select PLAYER_ID, PLAYER_NAME, BSP.GAME_DATE,
           sum(PTS) over W1 as TotalPoints,
           sum(MIN) over W1 as TotalMins,
           row_number() over W1 as GameNumber
    from BoxScoreP BSP
    where BSP.SEASON_TYPE=2 and MIN>0
    window W1 as (partition by PLAYER_ID order by GAME_DATE rows between unbounded preceding and current row)
    ),
    WithRatio as (
        select *,
               TotalPoints * 1.0 / TotalMins as PointsPerMinute
        from MinutedGames
    )
    select PLAYER_ID, PLAYER_NAME, PointsPerMinute, GAME_DATE
    from WithRatio
    where GameNumber >= 250
    order by GAME_DATE"""
    c = conn.cursor()
    data = c.execute(query)
    players_pers = heapdict()
    current_date = None
    results = [((None, None, None, None), (None, None, None, None))]
    for player_id, player_name, points_per_minute, game_date in data:
        if game_date != current_date:
            if current_date is not None:
                (max_player_id, max_player_name), max_pers = players_pers.peekitem()
                if results[-1][1][1] != max_player_id:
                    prev = results[-1][1]
                    if prev[1] is not None:
                        prev = (current_date, prev[1], prev[2], -players_pers[(prev[1], prev[2])])
                    results.append((prev, (current_date, max_player_id, max_player_name, -max_pers)))
            current_date = game_date
        players_pers[(player_id, player_name)] = -points_per_minute
    for (prev_date, prev_id, prev_name, prev_current_ppm), (cur_date, cur_id, cur_name, cur_current_ppm) in results:
        if cur_id is not None:
            print(f'{cur_date}:')
            if prev_id is not None:
                print(f'\t{cur_name}({cur_id}) passes {prev_name}({prev_id}):')
                print(f'\t\tprev record at date: {prev_current_ppm}.')
            else:
                print(f'\t{cur_name}({cur_id}) is the inaugural record holder:')
            print(f'\t\tnew record at date: {cur_current_ppm}.')
    (max_player_id, max_player_name), max_pers = players_pers.peekitem()
    print(f'current holder: {max_player_name}({max_player_id}) with {-max_pers} points per minute')
    conn.close()


if __name__ == '__main__':
    main()
