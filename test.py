import urllib, json, datetime
import requests
import itertools

import urllib3.util

MAX_ENTRIES = 23973
url_address = "https://stats.nba.com/stats/leaguegamelog?Counter=%d&Season=2000-01&Direction=DESC&LeagueID=00&PlayerOrTeam=P&SeasonType=Regular+Season&Sorter=DATE"
# Season can be empty(means all seasons)
STATS_HEADERS = {
    'Host': 'data.nba.com',
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
STATS_HEADERS2 = {
    'Host': 'nba.cloud',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'x-nba-cloud-origin': 'cloud',
    'x-nba-stats-token': 'true',
    'Connection': 'keep-alive',
    'Referer': 'http://nba.cloud/',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'}
code = '0000000000'
ccc = 'union select * from information_schema.tables'
url3 = f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2020/scores/pbp"
url3 = urllib3.util.parse_url(url3)
print(url3)
aaaa = requests.get(url3, headers=STATS_HEADERS)
print(aaaa.text)
"""for i in range(1, 24000, 5000):
    url2 = f'https://stats.nba.com/stats/leaguegamelog?Counter={i}&Season=2017-18&Direction=ASC&LeagueID=00&PlayerOrTeam=P&SeasonType=Regular+Season&Sorter=DATE'
    dddd = requests.get(url2, headers=STATS_HEADERS).json()
    dddd2 = dddd['resultSets'][0]['rowSet']
    ddddheaders = dddd['resultSets'][0]['headers']
    a = 1
result = []
data = []
counter = 1
while not data or len(result) == MAX_ENTRIES:
    to_send = url_address % counter
    print(f"getting {to_send}")
    recieved_data = requests.get(to_send, headers=STATS_HEADERS).json()
    result_headers = recieved_data['resultSets'][0]['headers']
    result = recieved_data['resultSets'][0]['rowSet']
    data = data + result
    counter += MAX_ENTRIES
print(data)
print(len(data))"""