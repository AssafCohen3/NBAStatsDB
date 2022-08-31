from sqlalchemy import select, func

from dbmanager.Database.Models.BoxScoreT import BoxScoreT


def collect_teams(session):
    teams_seasons_cte = (
        select(BoxScoreT.Season, BoxScoreT.TeamId, BoxScoreT.TeamAbbreviation, BoxScoreT.TeamName).
        group_by(BoxScoreT.Season, BoxScoreT.TeamId, BoxScoreT.TeamName, BoxScoreT.TeamAbbreviation).
        cte()
    )
    teams_seasons_with_previous_season_cte = (
        select(teams_seasons_cte,
               func.row_number().over(partition_by=[teams_seasons_cte.c.TeamId, teams_seasons_cte.c.TeamName, teams_seasons_cte.c.TeamAbbreviation],
                                      order_by=[teams_seasons_cte.c.Season]).label('SeasonNumber')).
        cte()
    )
    stmt = (
        select(teams_seasons_with_previous_season_cte.c.TeamId, teams_seasons_with_previous_season_cte.c.TeamAbbreviation, teams_seasons_with_previous_season_cte.c.TeamName,
               func.min(teams_seasons_with_previous_season_cte.c.Season).label('FirstSeason'),
               func.max(teams_seasons_with_previous_season_cte.c.Season).label('LastSeason')).
        group_by(teams_seasons_with_previous_season_cte.c.TeamId, teams_seasons_with_previous_season_cte.c.TeamAbbreviation, teams_seasons_with_previous_season_cte.c.TeamName,
                 teams_seasons_with_previous_season_cte.c.Season - teams_seasons_with_previous_season_cte.c.SeasonNumber).
        order_by('FirstSeason')
    )
    res = session.execute(stmt).fetchall()
    return res
