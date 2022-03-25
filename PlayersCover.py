import json
import heapq
import numpy
import numpy as np


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
    import cvxpy
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


def get_teams_cover(conn):
    teams_rosters = conn.execute("""
        with DISTINCT_PLAYER_TEAMS as (
            select distinct SEASON,
                            first_value(TEAM_ID) over (partition by SEASON, PLAYER_ID order by GAME_DATE desc) as LastTeamId,
                            PLAYER_ID,
                            PLAYER_NAME
            from BoxScoreP
            inner join Player on PLAYER_ID = Player.PlayerId
            where SEASON_TYPE=2 and Player.BirthDate is null
        )
        select SEASON, LastTeamId, json_group_array(PLAYER_ID)
        from DISTINCT_PLAYER_TEAMS
        group by SEASON, LastTeamId""").fetchall()
    teams_rosters = [(season, tid, json.loads(players)) for season, tid, players in teams_rosters]
    subsets = [((t[0], t[1]), set(t[2])) for t in teams_rosters]
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
