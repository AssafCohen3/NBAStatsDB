import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
from constants import *


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
    cmd = """select PS.PLAYER_ID, PS.PLAYER_NAME, count(distinct SerieStart) as SERIES_COUNT,
             sum(case PS.SHOULD_WON = 1 and PS.WON = 1 when true then 1 else 0 end) as FAVOURITE_WINS,
             sum(case PS.SHOULD_WON = 1 and PS.WON = 0 when true then 1 else 0 end) as FAVOURITE_LOSES,
             sum(case PS.SHOULD_LOST = 1 and PS.WON = 1 when true then 1 else 0 end) as UNDERDOG_WINS,
             sum(case PS.SHOULD_LOST = 1 and PS.WON = 0 when true then 1 else 0 end) as UNDERDOG_LOSES,
             sum(case PS.SHOULD_LOST = 1 and PS.WON = 1 when true then 1 else 0 end) - sum(case PS.SHOULD_WON = 1 and PS.WON = 0 when true then 1 else 0 end) as RATIO
      from PlayerSeriesWithOdds PS inner join Teams T on T.TEAM_ID = PS.TeamId and PS.SEASON <= T.LAST_USED and PS.SEASON >= T.FIRST_USED
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


def plot_average_win_percent_on_high_score(conn):
    df = pd.read_sql_query("""
    with HIGH_SCORE_GAMES as (
        select
               BoxScoreP.SEASON,
               PLAYER_ID, PLAYER_NAME, TEAM_NAME,
               PTS, GAME_DATE, TeamAName, TeamBName, TS.WinPercent               
        from BoxScoreP
            inner join TeamSeason TS on
                TS.SEASON = BoxScoreP.SEASON and
                ((BoxScoreP.TEAM_ID = TeamAId and TeamBId = TS.TEAM_ID) or
                 (BoxScoreP.TEAM_ID = TeamBId and TeamAId = TS.TEAM_ID))
        where PTS >= 50
        )
    select SEASON as Range, avg(WinPercent) * 100 as AVG_WIN_PCT from HIGH_SCORE_GAMES
    group by SEASON
    """, conn)
    df.plot(x='Range', y='AVG_WIN_PCT', kind='line')
    plt.show()


def plot_careers_averages_ranges(conn, range_size, from_season, until_season):
    sql = """with
     PlayersCareers as (
         select Player.*,
                min(SEASON) as FirstSeason,
                max(SEASON) as LastSeason,
                count(distinct SEASON) as SeasonsCount,
                min(GAME_DATE) as FirstGameDate,
                max(GAME_DATE) as LastGameDate
         from Player
            inner join BoxScoreP on PlayerId = PLAYER_ID
         group by PlayerId
     ),
     WithAges as (
         select PC.*,
                BPFIRST.AgeYears as AgeYearsFirst,
                BPFIRST.AgeDays as AgeDaysFirst,
                BPLAST.AgeYears as AgeYearsLast,
                BPLAST.AgeDays as AgeDaysLast
         from PlayersCareers PC
            inner join BoxScorePWithAge BPFIRST on PC.PlayerId = BPFIRST.PLAYER_ID and PC.FirstGameDate = BPFIRST.GAME_DATE
            inner join BoxScorePWithAge BPLAST on PC.PlayerId = BPLAST.PLAYER_ID and PC.LastGameDate = BPLAST.GAME_DATE
     ),
     CareersFullDetails as (
         select PlayerId,
                FullName,
                DraftYear,
                DraftRound,
                DraftNumber,
                FirstSeason,
                LastSeason,
                SeasonsCount,
                LastSeason - FirstSeason + 1 as CareerLength,
                AgeYearsFirst,
                AgeDaysFirst,
                AgeYearsLast,
                AgeDaysLast
         from WithAges
     ),
     RangeAverages as (
         select FirstSeason/:range_size * :range_size as Decade,
                min(FirstSeason) as FirstSeason,
                max(FirstSeason) as LastSeason,
                round(avg(FirstSeason), 2) as AverageFirstSeason,
                round(avg(LastSeason), 2) as AverageLastSeason,
                round(avg(SeasonsCount), 2) as AverageSeasonsCount,
                round(avg(CareerLength), 2) as AverageCareerLength,
                round(avg(AgeYearsFirst), 2) as AverageAgeYearsFirst,
                round(avg(AgeDaysFirst), 2) as AverageAgeDaysFirst,
                round(avg(AgeYearsLast), 2) as AverageAgeYearsLast,
                round(avg(AgeDaysLast), 2) as AverageAgeDaysLast
         from CareersFullDetails C
         where FirstSeason >= :from_season and FirstSeason <= :until_season
         group by FirstSeason / :range_size * :range_size
     ),
     IronManStats as (
         select SSC.SEASON, MaxGames as SeasonGames,
                round(avg(GAMES_PLAYED), 2) as AveragePlayerGames,
                sum(iif(GAMES_PLAYED = MaxGames, 1, 0)) as IronMansCount,
                avg(GAMES_PLAYED) * 1.0 / MaxGames as PlayRatio
         from PlayerSeasonFullStats
            inner join SeasonStatsCriteria SSC on PlayerSeasonFullStats.SEASON = SSC.SEASON
         group by PlayerSeasonFullStats.SEASON
     ),
     WithIronManStats as (
         select RAVG.*,
                count(*) as SeasonsCount,
                round(avg(SeasonGames), 2) as SeasonAverageGameCount,
                sum(IronMansCount) as TotalIronMans,
                round(avg(IronMansCount), 2) as AverageIronManCount
         from RangeAverages RAVG
            inner join IronManStats I on I.SEASON / :range_size * :range_size = RAVG.Decade
         group by Decade
     )
select Decade as Season,
       AverageIronManCount,
       AverageSeasonsCount,
       AverageCareerLength
from WithIronManStats
order by Season
    """
    df = pd.read_sql_query(sql, conn, params={'range_size': range_size, 'from_season': from_season, 'until_season': until_season})
    fig, ax = plt.subplots()
    df.plot(kind="line", ax=ax, x='Season', y='AverageSeasonsCount', legend=True, color='red', label='Average Seasons Count')
    ax.tick_params(axis='x', labelsize=8)
    plt.xlabel("")
    ax2 = ax.twinx()
    df.plot(kind="line", ax=ax2, x='Season', y='AverageIronManCount', legend=True, color='blue', label='Average Iron Mans')
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    ax.set_xlabel('Season')
    ax.set_ylabel('Average Career Length')
    ax2.set_ylabel('Average Iron Man Seasons')
    plt.title("Average Seasons(by Entrance year) vs \nAverage Iron Mans Seasons(Players to play all games)")
    fig.tight_layout()
    plt.show()


def plot_season_iron_mans(conn, range_size, from_season, until_season):
    sql = """with
     IronManStats as (
         select SSC.SEASON, MaxGames as SeasonGames,
                round(avg(GAMES_PLAYED), 2) as AveragePlayerGames,
                sum(iif(GAMES_PLAYED = MaxGames, 1, 0)) as IronMansCount,
                avg(GAMES_PLAYED) * 1.0 / MaxGames as PlayRatio
         from PlayerSeasonFullStats
            inner join SeasonStatsCriteria SSC on PlayerSeasonFullStats.SEASON = SSC.SEASON
         group by PlayerSeasonFullStats.SEASON
     ),
     WithIronManStats as (
         select SEASON / :range_size * :range_size as Range,
                count(*) as SeasonsCount,
                round(avg(SeasonGames), 2) as SeasonAverageGameCount,
                sum(IronMansCount) as TotalIronMans,
                round(avg(IronMansCount), 2) as AverageIronManCount
         from IronManStats RAVG
         where SEASON >= :from_season and SEASON <= :until_season
         group by SEASON / :range_size * :range_size
     )
select Range as Season,
       AverageIronManCount
from WithIronManStats
order by Season
    """
    df = pd.read_sql_query(sql, conn, params={'range_size': range_size, 'from_season': from_season, 'until_season': until_season})
    fig, ax = plt.subplots()
    df.plot(kind="line", ax=ax, x='Season', y='AverageIronManCount', legend=True, color='blue', label='Average Iron Mans')
    ax.tick_params(axis='x', labelsize=8)
    ax.set_xlabel('Season')
    plt.title("Average Iron Mans(Players to play all games)")
    fig.tight_layout()
    plt.show()


def plot_seasons_average_career_misc(conn):
    sql = """with
             PlayersCareers as (
                 select Player.*,
                        min(SEASON) as FirstSeason,
                        max(SEASON) as LastSeason,
                        count(distinct SEASON) as SeasonsCount,
                        min(GAME_DATE) as FirstGameDate,
                        max(GAME_DATE) as LastGameDate,
                        AC.APPEAREANCES
                 from Player
                    inner join BoxScoreP on PlayerId = BoxScoreP.PLAYER_ID
                    left join AllstarCareer AC on BoxScoreP.PLAYER_ID = AC.PLAYER_ID
                 group by Player.PlayerId
             ),
             RangeAverages as (
                 select FirstSeason/5 * 5 as Decade,
                        round(avg(SeasonsCount), 2) as AverageSeasonsCount,
                        count(*) as CareersCount,
                        round(avg(iif(SeasonsCount < 6, null, SeasonsCount)), 2) as AverageVeteransSeasonsCount,
                        sum(iif(SeasonsCount < 6, 0, 1)) as VeteransCount,
                        round(avg(iif(APPEAREANCES is null, null, SeasonsCount)), 2) as AverageAllstarsSeasonsCount,
                        sum(iif(APPEAREANCES is null, 0, 1)) as AllstarsCount
                 from PlayersCareers C
                 group by FirstSeason / 5 * 5
             )
        select Decade as Season,
               AverageSeasonsCount, CareersCount,
               AverageVeteransSeasonsCount, VeteransCount,
               AverageAllstarsSeasonsCount, AllstarsCount
        from RangeAverages
        where Decade < 2010
        order by Season"""
    df = pd.read_sql_query(sql, conn)
    fig, ax = plt.subplots()
    df.plot(kind="line", ax=ax, x='Season', y=['AverageSeasonsCount', 'AverageVeteransSeasonsCount', 'AverageAllstarsSeasonsCount'])
    ax.legend(['All players', 'Veterans(6 seasons+)', 'Allstars'])
    ax.tick_params(axis='x', labelsize=8)
    ax.set_xlabel('Season')
    plt.title("Average Career Length(splits)\nlabeled with qualified careers number")
    for idx, row in df.iterrows():
        ax.annotate(int(row['CareersCount']), (row['Season'] - 0.35, row['AverageSeasonsCount'] + 0.2), fontsize=6)
        ax.annotate(int(row['VeteransCount']), (row['Season'] - 0.35, row['AverageVeteransSeasonsCount'] + 0.2), fontsize=6)
        ax.annotate(int(row['AllstarsCount']), (row['Season'] - 0.35, row['AverageAllstarsSeasonsCount'] + 0.2), fontsize=6)
    fig.tight_layout()
    plt.show()


def plot_seasons_average_miss(conn):
    sql = """with
                PlayersGames as (
                    select BoxScoreP.Season, PlayerId, PlayerName,
                           count(*) as GamesNumber,
                           SSC.MaxGames as SeasonGames,
                           100 - (count(*)*100.0/MaxGames) as MissingGamesPercent
                    from BoxScoreP
                        inner join SeasonStatsCriteria SSC on BoxScoreP.Season = SSC.Season
                    where SeasonType=2
                    group by BoxScoreP.Season, PlayerId
                ),
                WithAwards as (
                    select P.*,
                           max(A.Season) as AllNBASeason,
                           max(AP.Season) as AllStarSeason
                    from PlayersGames P
                        left join Awards A on A.Season between P.Season-1 and P.Season and A.Description='All-NBA' and A.PlayerId=P.PlayerId
                        left join BoxScoreP AP on AP.PlayerId=P.PlayerId and AP.Season between P.Season-1 and P.Season and AP.SeasonType=3
                    group by P.PlayerId, P.Season
                ),
                BySeasons as (
                    select Season,
                           SeasonGames,
                           count(*) as PlayersAboveCriteria,
                           count(*) filter ( where AllNBASeason is not null or AllStarSeason is not null) as StartAboveCriteria,
                           avg(MissingGamesPercent) as AverageMissingGamesPercent,
                           avg(MissingGamesPercent) filter ( where AllNBASeason is not null or AllStarSeason is not null) as AverageStarsMissingGamesPercent
                    from WithAwards
                    where GamesNumber >= SeasonGames*0.25
                    group by Season
                ),
                ByPeriod as (
                    select (Season/5) * 5 as Season,
                           count(*) as SeasonsCount,
                           avg(AverageMissingGamesPercent) as AverageMissingGamesPercent,
                           avg(AverageStarsMissingGamesPercent) as AverageStarsMissingGamesPercent
                    from BySeasons
                    group by (Season/5) * 5
                )
            select *
            from ByPeriod"""
    df = pd.read_sql_query(sql, conn)
    fig, ax = plt.subplots()
    df.plot(kind="line", ax=ax, x='Season', y=['AverageMissingGamesPercent', 'AverageStarsMissingGamesPercent'])
    ax.legend(['All players', 'Stars(AllStar or All-NBA in the last 2 seasons)'])
    ax.tick_params(axis='x', labelsize=8)
    ax.set_xlabel('Season')
    ax.set_ylabel('Average % of missed games')
    plt.title("Average % of missed games by players.\n(players who played more than 1/4 of possible games)")
    # for idx, row in df.iterrows():
    #     ax.annotate(int(row['AverageMissingGames']), (row['Season'] - 0.35, row['AverageMissingGames'] + 0.2), fontsize=6)
    #     ax.annotate(int(row['AverageStarsMissingGames']), (row['Season'] - 0.35, row['AverageStarsMissingGames'] + 0.2), fontsize=6)
    fig.tight_layout()
    plt.show()


def get_connection():
    return sqlite3.connect(DATABASE_PATH + DATABASE_NAME_NEW + '.sqlite')


def main():
    conn = get_connection()
    plot_seasons_average_miss(conn)


if __name__ == '__main__':
    main()