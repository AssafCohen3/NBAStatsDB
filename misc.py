import matplotlib as plt
import pandas as pd


# get average career length
# example: get_most_seasons_avg(conn, 10, 5, 1970) will return for each decade starts from the 70s the average career length
# of players who played for more than 5 seasons
def get_most_seasons_avg(conn, seasons_range, min_career, max_season):
    statement = """select (PC.FIRST_SEASON/ :range * :range) as season, round(avg(SeasonsAt), 2) as AverageMostSeasonsAtTeam
                    from PlayerTeamMostSeasons PTMS join PlayerCareer PC on PTMS.PLAYER_ID = PC.PLAYER_ID
                    where PC.SEASONS_NUM >= :min_career and season <= :max_season group by PC.FIRST_SEASON/:range * :range
"""
    cur = conn.cursor()
    cur.execute(statement, {"range": seasons_range, "min_career": min_career, "max_season": max_season})
    rows = cur.fetchall()
    return rows


def get_adjusted_teams_avg(conn, seasons_range, min_career, max_season):
    statement = """select (FirstYear / :range) * :range as SEASON, round(avg(AdjustedTeamNumber), 2) as AverageAdjustedTeamsNumber from PlayerAdjustedTeamsNumber
                    where SEASON <= :max_season and CareerLength >= :min_career
                    group by (FirstYear / :range) * :range
"""
    cur = conn.cursor()
    cur.execute(statement, {"range": seasons_range, "min_career": min_career, "max_season": max_season})
    rows = cur.fetchall()
    return rows


def get_teams_avg(conn, seasons_range, min_career, max_season):
    statement = """select (FirstYear / :range) * :range as SEASON, round(avg(PlayerTeamNumber), 2) as AverageAdjustedTeamsNumber from PlayerAdjustedTeamsNumber
                    where SEASON <= :max_season and CareerLength >= :min_career
                    group by (FirstYear / :range) * :range
"""

    cur = conn.cursor()
    cur.execute(statement, {"range": seasons_range, "min_career": min_career, "max_season": max_season})
    rows = cur.fetchall()
    return rows


def plot_average_most_seasons(conn):
    res_rows = get_most_seasons_avg(conn, 5, 5, 2010)
    points = [(row[0], row[1]) for row in res_rows]
    print(points)
    plt.scatter(*zip(*points))
    plt.ylim(0, 10)
    plt.show()


def plot_average_player_teams_number(conn):
    average_teams_number = get_teams_avg(conn, 5, 5, 2005)
    adjusted_average_teams_number = get_adjusted_teams_avg(conn, 5, 5, 2005)
    average_teams_points = [(row[0], row[1]) for row in average_teams_number]
    adjusted_average_teams_points = [(row[0], row[1]) for row in adjusted_average_teams_number]
    print(f"{average_teams_points=}")
    print(f"{adjusted_average_teams_points=}")
    plt.scatter(*zip(*average_teams_points), color='blue', label="regular average")
    plt.scatter(*zip(*adjusted_average_teams_points), color='red', label="adjusted average")
    plt.legend()
    plt.ylim(0, 10)
    plt.show()


def triple_doubles_record(conn):
    cmd = """
        select
           PLAYER_NAME,
           sum(case when WL = 'W' then 1 else 0 end) as wins,
           sum(case when WL = 'L' then 1 else 0 end) as loses
           from BoxScoreP
        where
            case when PTS >= 10 then 1 else 0 end +
            case when REB >= 10 then 1 else 0 end +
            case when AST >= 10 then 1 else 0 end +
            case when STL >= 10 then 1 else 0 end +
            case when BLK >= 10 then 1 else 0 end >= 3
        group by PLAYER_ID
        order by count(*) desc
        """
    df = pd.read_sql_query(cmd, conn, index_col='PLAYER_NAME')
    return df


def plot_triple_double_record(df, limit):
    sum_row = df.sum(numeric_only=True)
    df = df[:limit]
    df.loc["Total"] = sum_row
    # this will contain the data for the second y-axis
    df2 = df.copy()
    # this will contain the data for the first y-axis
    df.at["Total"] = [0, 0]

    fig, ax = plt.subplots()
    df.plot(kind="bar", stacked=True, legend=False, ax=ax)
    ax.tick_params(axis='x', labelsize=8)
    plt.xlabel("")

    # calculate total games and percentages for each row
    df_total = df2["wins"] + df2["loses"]
    df_rel = df2[df2.columns[0]].div(df_total, 0) * 100

    # zero all rows except total for the second y-axis
    df2[df.index != "Total"] = [0, 0]
    ax2 = ax.twinx()
    df2.plot(kind="bar", stacked=True, ax=ax2, legend=False)

    plt.title("Triple doubles split - top 25")
    fig.tight_layout()

    # add percentages above bars
    for i, v in enumerate(df_total):
        ax.text(x=i-0.35, y=v+1, s=f"{int(df_rel[i])}%", fontdict={"fontsize": 6})
    ax2.text(x=limit - 0.35, y=df_total[limit] + 1, s=f"{int(df_rel[limit])}%", fontdict={"fontsize": 6})
    # ax.legend(loc='center left', bbox_to_anchor=(1,0.5))

    plt.show()


def get_underdog_data(conn, min_threshold):
    cmd = """select PS.PLAYER_ID, PS.PLAYER_NAME, count(distinct SERIES_START) as SERIES_COUNT,
             sum(case PS.SHOULD_WON = 1 and PS.WON = 1 when true then 1 else 0 end) as FAVOURITE_WINS,
             sum(case PS.SHOULD_WON = 1 and PS.WON = 0 when true then 1 else 0 end) as FAVOURITE_LOSES,
             sum(case PS.SHOULD_LOST = 1 and PS.WON = 1 when true then 1 else 0 end) as UNDERDOG_WINS,
             sum(case PS.SHOULD_LOST = 1 and PS.WON = 0 when true then 1 else 0 end) as UNDERDOG_LOSES,
             sum(case PS.SHOULD_LOST = 1 and PS.WON = 1 when true then 1 else 0 end) - sum(case PS.SHOULD_WON = 1 and PS.WON = 0 when true then 1 else 0 end) as RATIO
      from PlayerSeriesWithOdds PS inner join Teams T on T.TEAM_ABBREVIATION = PS.TEAM_SERIE and PS.SEASON <= T.LAST_USED and PS.SEASON >= T.FIRST_USED
      where AVG_MIN >= :minimum_minutes
      group by PS.PLAYER_ID
      order by SERIES_COUNT desc"""
    cur = conn.cursor()
    cur.execute(cmd, {"minimum_minutes": min_threshold})
    rows = cur.fetchall()
    return rows


def differ(list1, list2):
    differ_list = [x for x in list2 if x not in list1]
    print(differ_list)
