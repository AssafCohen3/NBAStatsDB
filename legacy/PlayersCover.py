import heapq
from collections import defaultdict
import numpy
import numpy as np
if False or None:
    import cvxpy


# for franchise in {Boston, Atlanta, ...}, year in {2021, 2020, ...} define team(franchise, year) as the roster of the franchise at the end of the year
# create matrix of players. each row represent a player and each column represent a team. x[i][j] = 1 iff player i played in team j
def create_matrix(teams_rosters):
    rows = {}
    for i, (season, tid, players) in enumerate(teams_rosters):
        for p in players:
            if p not in rows:
                rows[p] = [0] * len(teams_rosters)
            rows[p][i] = 1
    return [(t[:-1], 0) for t in teams_rosters], numpy.array(list(rows.values()))


# a test with linear programming. thats improve the solution only by 50 teams so the greedy is enough
def linear_programming(teams_rosters):
    columns, players_rows = create_matrix(teams_rosters)
    selection = cvxpy.Variable(len(teams_rosters), boolean=True)
    b = np.full(players_rows.shape[0], 1)
    c = np.full(len(teams_rosters), 1)
    prob = cvxpy.Problem(cvxpy.Minimize(c.T@selection),
                         [players_rows @ selection >= b])
    prob.solve(solver=cvxpy.GLPK_MI)
    print("\nThe optimal value is", prob.value)
    print("A solution x is")
    print(selection.value)
    print("A dual solution is")
    print(prob.constraints[0].dual_value)


def get_teams_cover(players_last_team):
    # players_last_team = conn.execute("""
    #     with DISTINCT_PLAYER_TEAMS as (
    #         select distinct SEASON,
    #                         first_value(TEAM_ID) over (partition by SEASON, PLAYER_ID order by GAME_DATE desc) as LastTeamId,
    #                         PLAYER_ID,
    #                         PLAYER_NAME
    #         from BoxScoreP
    #         inner join Player on PLAYER_ID = Player.PlayerId
    #         where SEASON_TYPE=2 and Player.BirthDate is null
    #     )
    #     select SEASON, LastTeamId, PLAYER_ID
    #     from DISTINCT_PLAYER_TEAMS""").fetchall()
    teams_rosters = defaultdict(set)
    for season, last_team_id, player_id in players_last_team:
        teams_rosters[(season, last_team_id)].add(player_id)
    subsets = teams_rosters.items()
    all_players = set([p for t in subsets for p in t[1]])
    res = greedy_set_cover(subsets, all_players)
    teams_to_ret = [(t[1], t[0]) for t in res]
    return sorted(teams_to_ret)


def greedy_set_cover(subsets, parent_set):
    parent_set = set(parent_set)
    max_set_len = len(parent_set)
    heap = []
    for s_id, s in subsets:
        heapq.heappush(heap, [max_set_len-len(s), len(heap), (s, s_id)])
    results = []
    result_set = set()
    while result_set < parent_set:
        best = []
        unused = []
        while heap:
            score, count, (s, s_id) = heapq.heappop(heap)
            if not best:
                best = [max_set_len-len(s - result_set), count, (s, s_id)]
                continue
            if score >= best[0]:
                heapq.heappush(heap, [score, count, (s, s_id)])
                break
            score = max_set_len-len(s - result_set)
            if score >= best[0]:
                unused.append([score, count, (s, s_id)])
            else:
                unused.append(best)
                best = [score, count, (s, s_id)]
        add_set, s_id = best[2]
        results.append((add_set, s_id))
        result_set.update(add_set)
        while unused:
            heapq.heappush(heap, unused.pop())
    return results
