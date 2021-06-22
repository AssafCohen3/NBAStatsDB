import urllib.request, json, datetime
teamsAddress = "http://data.nba.net/prod/v1/2019/teams.json"
urlAddress = "http://data.nba.net/prod/v2/2019/schedule.json"

with urllib.request.urlopen(urlAddress) as url:
    data = json.loads(url.read().decode())
with urllib.request.urlopen(teamsAddress) as url:
    teams = json.loads(url.read().decode())
teams = dict((team["teamId"],team) for team in list(filter(lambda team: team["isNBAFranchise"] ,teams["league"]["standard"])))
dateFormat = "%Y%m%d"
start_date = datetime.datetime.now() - datetime.timedelta(days=16)
data = list(filter(lambda game: datetime.datetime.strptime(game["startDateEastern"],dateFormat) >= start_date and game["statusNum"] == 3,data["league"]["standard"]))
infectedTeams = {'1610612762'}
for game in data:
    hTeamId = game["hTeam"]["teamId"]
    vTeamId = game["vTeam"]["teamId"]
    if(hTeamId in infectedTeams or vTeamId in infectedTeams):
        infectedTeams.add(hTeamId)
        infectedTeams.add(vTeamId)
finalNames = {teams[id]["fullName"] for id in infectedTeams}
allNames = {val["fullName"] for val in teams.values()}
dif = allNames - finalNames
print("All teams: ")
print(allNames)
print("infected Teams:")
print(finalNames)
print("not infected:")
print(dif)