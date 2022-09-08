import heapq
import time
from collections import defaultdict
from datetime import datetime

from alive_progress import alive_it
from sqlalchemy import update, bindparam, func, and_
from sqlalchemy.sql import select

from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Database.Models.NBAPlayer import Player
from dbmanager.Downloaders.PlayerProfileHandler import PlayerProfileHandler
from dbmanager.Downloaders.TeamRosterHandler import TeamRosterHandler
from dbmanager.MainRequestsSession import call_with_retry
from dbmanager.Resources.ResourceAbc import ResourceAbc
from dbmanager.constants import STATS_DELAY_SECONDS


class PlayerBirthdateResourceHandler(ResourceAbc):

    def get_teams_cover(self):
        teams_rosters = defaultdict(set)
        for season, last_team_id, player_id in self.get_players_last_team_to_cover():
            teams_rosters[(season, last_team_id)].add(player_id)
        subsets = teams_rosters.items()
        all_players = set([p for t in subsets for p in t[1]])
        res = self.greedy_set_cover(subsets, all_players)
        teams_to_ret = [(t[1], t[0]) for t in res]
        return sorted(teams_to_ret)

    @staticmethod
    def greedy_set_cover(subsets, parent_set):
        parent_set = set(parent_set)
        max_set_len = len(parent_set)
        heap = []
        for s_id, s in subsets:
            heapq.heappush(heap, [max_set_len - len(s), len(heap), (s, s_id)])
        results = []
        result_set = set()
        while result_set < parent_set:
            best = []
            unused = []
            while heap:
                score, count, (s, s_id) = heapq.heappop(heap)
                if not best:
                    best = [max_set_len - len(s - result_set), count, (s, s_id)]
                    continue
                if score >= best[0]:
                    heapq.heappush(heap, [score, count, (s, s_id)])
                    break
                score = max_set_len - len(s - result_set)
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

    def get_players_last_team_to_cover(self):
        distinct_player_teams_cte = (
            select(BoxScoreP.Season,
                   func.first_value(BoxScoreP.TeamId).over(partition_by=[BoxScoreP.Season, BoxScoreP.PlayerId], order_by=[BoxScoreP.GameDate.desc()]).label('LastTeamId'),
                   BoxScoreP.PlayerId,
                   BoxScoreP.PlayerName).
            join(Player, BoxScoreP.PlayerId == Player.PlayerId).
            where(and_(BoxScoreP.SeasonType.in_([2, 4]), Player.BirthDate.is_(None))).
            distinct().
            cte()
        )
        stmt = select(distinct_player_teams_cte.c.Season, distinct_player_teams_cte.c.LastTeamId, distinct_player_teams_cte.c.PlayerId)
        return self.session.execute(stmt).fetchall()

    def update_players_birthdate(self, players_birthdates):
        if not players_birthdates:
            return
        stmt = (
            update(Player).
            where(Player.PlayerId == bindparam('PlayerIdToUpdate')).
            values(
                BirthDate=bindparam('NewBirthDate')
            )
        )
        self.session.execute(stmt, players_birthdates)
        self.session.commit()

    def update_players_birthdates(self):
        # this for some reason exist only in the player profile endpoint and the team roster endpoint.
        # instead of making a request for each player try to find a set of teams rosters which contains all players
        # this reduce the request to something around 1000(instead of 4000)
        print('updating players birthdates')
        teams_cover = self.get_teams_cover()
        if len(teams_cover) == 0:
            return
        print(f'{len(teams_cover)} teams to cover...')
        for (season, tid), expected_players in alive_it(teams_cover, force_tty=True, title='Fetching Teams Rosters', enrich_print=False):
            handler = TeamRosterHandler(season, tid)
            data = call_with_retry(handler.downloader, 2)
            if not data:
                print(f'could not fetch roster of {season} {tid}.')
                continue
            data = data['resultSets'][0]['rowSet']
            players = [{'NewBirthDate': datetime.strptime(p[10], '%b %d, %Y').date(), 'PlayerIdToUpdate': p[14]} for p in data]
            self.update_players_birthdate(players)
            time.sleep(STATS_DELAY_SECONDS)  # sleep to prevent ban
        stmt = select(Player.PlayerId, Player.FullName).where(Player.BirthDate.is_(None))
        uncovered_players = self.session.execute(stmt).fetchall()
        if len(uncovered_players) == 0:
            return
        print(f'{len(uncovered_players)} players not covered. starting profile requests...')
        to_iterate = alive_it(uncovered_players, force_tty=True, title="Fetching Players profiles", enrich_print=False, dual_line=True)
        for (pid, pname) in to_iterate:
            to_iterate.text(f'-> Fetching {pname} birthdate...')
            handler = PlayerProfileHandler(pid)
            data = call_with_retry(handler.downloader, 2)
            if not data:
                print(f'could not fetch {pname} profile. try again later')
                continue
            data = data['resultSets'][0]['rowSet']
            self.update_players_birthdate([{'NewBirthDate': datetime.fromisoformat(data[0][7]).date(), 'PlayerIdToUpdate': data[0][0]}])
            time.sleep(STATS_DELAY_SECONDS)  # sleep to prevent ban
