import sqlite3

import heapdict
from heapdict import heapdict
from pandas._libs.internals import defaultdict

from constants import *


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
    results = []
    for player_id, player_name, points_per_minute, game_date in data:
        if game_date != current_date:
            if current_date is not None:
                (max_player_id, max_player_name), max_pers = players_pers.peekitem()
                if not results or results[-1][1] != max_player_id:
                    results.append((current_date, max_player_id, max_player_name, -max_pers))
            current_date = game_date
        players_pers[(player_id, player_name)] = -points_per_minute
    print('\n'.join(list(map(str, results))))


if __name__ == '__main__':
    main()
