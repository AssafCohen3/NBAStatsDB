import re
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from dbmanager.Handlers.BREFPlayers import BREFPlayerHandler


def get_player_stats_id(player_url):
    player_resp = requests.get(player_url).text
    player_soup = BeautifulSoup(player_resp, 'html.parser')
    player_birth_date = player_soup.select('span#necro-birth')[0]['data-birth']
    nba_stats_links = player_soup.select('#div_stats-nba-com a')
    player_stats_id = None
    for nba_stats_link in nba_stats_links:
        link_href = nba_stats_link['href']
        player_id_regex = re.findall(r'stats.nba.com/player/(.+?)/', link_href)
        if len(player_id_regex) > 0:
            player_stats_id = int(player_id_regex[0])
            break
    return player_stats_id, player_birth_date


def find_season_players_links(season):
    url = 'https://www.basketball-reference.com/leagues/NBA_%s_rookies.html' % (season + 1)
    resp = requests.get(url).text
    soup = BeautifulSoup(resp, 'html.parser')
    player_ids = soup.select('table#rookies tbody tr td[data-stat="player"]')
    player_ids = [(p['data-append-csv'],
                   unidecode(p.select('a')[0].getText().strip()),
                   'https://www.basketball-reference.com' + p.select('a')[0]['href']) for p in player_ids]
    return player_ids


def find_draft_players_links(season):
    url = 'https://www.basketball-reference.com/draft/NBA_%s.html' % season
    resp = requests.get(url).text
    soup = BeautifulSoup(resp, 'html.parser')
    player_ids = soup.select('table#stats tbody tr td[data-stat="player"]')
    player_ids = [(re.findall(r'/players/./(.+?)\.html', p.select('a')[0]['href'])[0],
                   unidecode(p.select('a')[0].getText().strip()),
                   'https://www.basketball-reference.com' + p.select('a')[0]['href']) for p in player_ids]
    return player_ids


def find_targets(resource_year, resource_type, target_ids):
    resource_players_links = find_season_players_links(resource_year) if resource_type == 'season' else find_draft_players_links(resource_year)
    to_ret = []
    for player_id, player_name, player_link in resource_players_links:
        player_stats_id, player_birth_date = get_player_stats_id(player_link)
        if player_stats_id and player_stats_id in target_ids:
            to_ret.append([player_stats_id, target_ids[player_stats_id], None, player_id, player_name, player_birth_date])
    return to_ret


def save_new_mappings(conn, mappings):
    conn.executeall("""insert or ignore into PlayerMapping (PlayerNbaId, PlayerNbaName, PlayerNbaBirthDate, PlayerBrefId, PlayerBrefName, PlayerBrefBirthDate) 
    values (?, ?, ?, ?, ?, ?)""", mappings)
    conn.commit()


def save_new_bref_players(conn, players):
    conn.executeall("""insert or ignore into BREFPlayer (PlayerId, PlayerName, FromYear, ToYear, Position, Height, Weight, Birthdate, Active, HOF) 
    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", players)
    conn.commit()


def complete_missing_mapping(conn):
    missing_mapping_sql = """with
                AllPlayersIds as (
                    select PLAYER_ID
                    from BoxScoreP
                    where SEASON >= 2021
                    --union
                    --select PlayerId
                    --from Player                    
                ),
                MissingPlayers as (
                    select PLAYER_ID
                    from AllPlayersIds P
                        left join PlayerMapping PM on PM.PlayerNbaId=P.PLAYER_ID
                    where PM.PlayerNbaId is null or true
                )
            select MP.PLAYER_ID, coalesce(BSP.PLAYER_NAME, P.FullName), coalesce(min(BSP.SEASON), DraftYear) as ResourceYear, iif(min(BSP.SEASON) is null, 'draft', 'season')
            from MissingPlayers MP
                left join BoxScoreP BSP on MP.PLAYER_ID=BSP.PLAYER_ID
                left join Player P on P.PlayerId=MP.PLAYER_ID
            group by MP.PLAYER_ID
            having ResourceYear is not null"""
    missing_mapping = conn.execute(missing_mapping_sql).fetchall()
    resources_to_fetch = defaultdict(dict)
    for missing_player_id, missing_player_name, resource_year, resource_type in missing_mapping:
        resources_to_fetch[(resource_year, resource_type)][missing_player_id] = missing_player_name
    for (resource_year, resource_type), targets in resources_to_fetch.items():
        new_mappings = find_targets(resource_year, resource_type, targets)
        # save_new_mappings(conn, new_mappings)


def complete_missing_players_data(conn):
    missing_player_data_sql = """
        with
            MissingPlayers as (
                select PM.PlayerBrefId
                from PlayerMapping PM
                    left join BREFPlayer BP on PM.PlayerBrefId=BP.PlayerId
                    left join BoxScoreP BSP on PM.PlayerNbaId=BSP.PLAYER_ID
                where BP.PlayerId is null or true
                group by PM.PlayerNbaId
                having count(BSP.GAME_ID) > 0 and min(BSP.SEASON) >= 2021
            )
        select distinct substring(PlayerBrefId, 1, 1)
        from MissingPlayers"""
    missing_letters = conn.execute(missing_player_data_sql).fetchall()
    for (letter, ) in missing_letters:
        handler = BREFPlayerHandler(letter)
        to_save = handler.downloader()
        # save_new_bref_players(conn, to_save)


def complete_bref(conn):
    complete_missing_mapping(conn)
    complete_missing_players_data(conn)
