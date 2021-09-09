import datetime
import sqlite3
import json
import os
import pandas as pd
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

url_address_date = "https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=%s&DateTo=&Direction=ASC&LeagueID=00&PlayerOrTeam=%s&Season=ALLTIME&SeasonType=%s&Sorter=DATE"
url_address_odds = "https://www.sportsoddshistory.com/nba-main/?y=%s&sa=nba&a=finals&o=r"
STATS_HEADERS = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true',
        'Connection': 'keep-alive',
        'Referer': 'https://stats.nba.com/',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'}
SEASON_TYPES = [
    "Regular+Season",
    "Playoffs",
    "All+Star"
]
DATABASE_NAME = "boxscores_full_database"
API_COUNT_THRESHOLD = 30000
files_template_quick = "quick_cache/boxscore_%s_%s_%s.json"
odds_files_template = "quick_cache/odds_%s.html"


def create_data_frame(data, headers):
    return pd.DataFrame(data=data, columns=headers)


def handle_cache(cache_handler, filename_template, load_file, downloader, cacher, *args):
    file_name = cache_handler.get_filename()
    if os.path.isfile(file_name):
        print(f"found {file_name} in cache.")
        with open(file_name, "rb") as f:
            to_ret = load_file(f)
    else:
        to_ret = downloader(args)
        print(f"Downloaded {file_name}.")
        with open(file_name, "w") as f2:
            f2.write(to_ret)
        print(f"Cached {file_name}.")
    return to_ret

def get_cached_odds(season):
    file_name = odds_files_template % season
    if os.path.isfile(file_name):
        print(f"found {file_name} in cache.")
        with open(file_name, "rb") as f:
            to_ret = f.read()
    else:
        to_send = url_address_odds % f"{season}-{season + 1}"
        to_ret = requests.get(to_send, headers=STATS_HEADERS).text
        print(f"Downloaded {file_name}.")
        with open(file_name, "w") as f2:
            f2.write(to_ret)
        print(f"Cached {file_name}.")
    return to_ret


def get_cached_boxscores(date_from, season_type_index, box_score_type):
    date_tmp = date_from
    if date_tmp == "":
        date_tmp = "first"
    file_name = files_tempplate_quick % (date_tmp, season_type_index, box_score_type)
    if os.path.isfile(file_name):
        print(f"found {file_name} in cache.")
        with open(file_name, "rb") as f:
            to_ret = json.load(f)
    else:
        to_send = url_address_date % (date_from, box_score_type, SEASON_TYPES[season_type_index])
        to_ret = requests.get(to_send, headers=STATS_HEADERS).json()
        data = to_ret["resultSets"][0]
        results = data["rowSet"]
        print(f"Downloaded {file_name}.")
        if len(results) >= API_COUNT_THRESHOLD:
            with open(file_name, "w") as f2:
                json.dump(to_ret, f2)
            print(f"Cached {file_name}.")
    return to_ret


def collect_all_boxscores(season_type_index, box_score_type):
    df = None
    date_from = ""
    continue_loop = True
    while continue_loop:
        data = get_cached_boxscores(date_from, season_type_index, box_score_type)
        data = data["resultSets"][0]
        headers = data["headers"]
        results = data["rowSet"]
        print(f"found {len(results)} games in {SEASON_TYPES[season_type_index].replace('+', ' ')} of type {box_score_type} from date {date_from}")
        if len(results) >= API_COUNT_THRESHOLD:
            game_date_index = headers.index("GAME_DATE")
            count = 0
            last_date = results[-1][game_date_index]
            while results[-1][game_date_index] == last_date:
                results.pop()
                count = count+1
            print(f"popped last {count} items.")
            date_from = last_date
        else:
            continue_loop = False
        new_df = create_data_frame(results, headers)
        df = new_df if df is None else pd.concat([df, new_df], ignore_index=True)
    return df


def add_sorted_teams_matchups(df):
    matchup_re_str = r'(.*) (?:@|vs.) (.*)'
    a = df['MATCHUP'].str.extract(matchup_re_str)
    a = a.to_numpy()
    a.sort(axis=1)
    a = pd.DataFrame(data=a, columns=["team1", "team2"])
    df["MATCHUP_TEAM1"] = a["team1"]
    df["MATCHUP_TEAM2"] = a["team2"]


def create_boxscores_table(conn, box_score_type):
    all_boxscores_df = None
    for i in range(0, len(SEASON_TYPES)):
        new_df = collect_all_boxscores(i, box_score_type)
        all_boxscores_df = new_df if all_boxscores_df is None else pd.concat([all_boxscores_df, new_df], ignore_index=True)
    season_and_type = all_boxscores_df["SEASON_ID"].str.extract(r'(\d)(\d*)')
    all_boxscores_df["SEASON_TYPE"] = season_and_type[0]
    all_boxscores_df["SEASON"] = season_and_type[1]
    add_sorted_teams_matchups(all_boxscores_df)
    all_boxscores_df.to_sql(f'BoxScore{box_score_type}', conn, if_exists='replace', index=False)


def get_connection():
    return sqlite3.connect(f"Database/{DATABASE_NAME}.sqlite")


def create_database():
    conn = get_connection()
    create_boxscores_table(conn, "P")
    create_boxscores_table(conn, "T")
    conn.commit()


def get_most_seasons_avg(conn, seasons_range, min_career, max_season):
    statement = """select (PC.FirstYear/ :range * :range) as season, round(avg(SeasonsAt), 2) as AverageMostSeasonsAtTeam
                    from PlayerTeamMostSeasons PTMS join PlayerCareer PC on PTMS.PLAYER_ID = PC.PLAYER_ID
                    where PC.CareerLength >= :min_career and season <= :max_season group by PC.FirstYear/:range * :range
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


def plot_average_most_seasons():
    conn = get_connection()
    res_rows = get_most_seasons_avg(conn, 5, 5, 2010)
    points = [(row[0], row[1]) for row in res_rows]
    print(points)
    plt.scatter(*zip(*points))
    plt.ylim(0, 10)
    plt.show()


def plot_average_player_teams_number():
    conn = get_connection()
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


def differ(list1, list2):
    differ_list = [x for x in list2 if x not in list1]
    print(differ_list)


def scrape_odds():
    url_address = "https://www.sportsoddshistory.com/nba-main/?y=1972-1973&sa=nba&a=finals&o=r"
    r = requests.get(url_address)
    df = None
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', {"class": "soh1"})
        df = pd.read_html(str(table))[0]
        print(df)
        a = 0

def test():
    url_address = "https://stats.nba.com/stats/commonplayoffseries?LeagueID=00&Season=1946-47&SeriesID="
    res = requests.get(url_address, headers=STATS_HEADERS).json()
    data = res["resultSets"][0]
    results = data["rowSet"]
    a = 0

print("Boxscore DB: Select algorithm")
scrape_odds()