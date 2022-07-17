import time
from MainRequestsSession import call_with_retry
from datetime import datetime
from alive_progress import alive_it
from sqlalchemy import func
from sqlalchemy.sql import select
from Database.Models.Awards import Awards
from Database.Models.BoxScoreP import BoxScoreP
from Database.Models.BoxScoreT import BoxScoreT
from Database.Models.Player import Player
from Handlers.PlayerAwardsHandler import PlayerAwardsHandler
from Handlers.TeamDetailsHandler import TeamDetailsHandler
from Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert
from constants import STATS_DELAY_SECONDS


class AwardsResourceHandler(ResourceAbc):

    def __init__(self, session, teams_spans):
        self.awards_headers = [
            'PlayerId',
            'FullName',
            'Jersey',
            'Position',
            'TeamId',
            'TeamName',
            'Description',
            'AllNBATeamNumber',
            'Season',
            'DateAwarded',
            'Confrence',
            'AwardType',
            'SubTypeA',
            'SubTypeB',
            'SubTypeC'
        ]
        self.teams_spans = teams_spans
        super().__init__(session)

    def get_teams_ids_and_last_name(self):
        stmt = select(BoxScoreT.TeamId, func.first_value(BoxScoreT.TeamName)
                      .over(partition_by=[BoxScoreT.TeamId],
                            order_by=[BoxScoreT.GameDate.desc()])).distinct()
        return self.session.execute(stmt).fetchall()

    def get_players_ids_and_names(self):
        stmt = select(Player.PlayerId, Player.FullName).distinct()
        return self.session.execute(stmt).fetchall()

    def get_active_players_ids_and_names(self):
        # get players who played a game in the last two seasons
        last_season_stmt = select(BoxScoreT.Season).order_by(BoxScoreT.GameDate.desc()).limit(1)
        last_season = self.session.execute(last_season_stmt).fetchall()[0][0]
        stmt = (
            select(BoxScoreP.PlayerId, BoxScoreP.PlayerName).
            where(BoxScoreP.Season >= last_season - 1).
            distinct()
        )
        return self.session.execute(stmt).fetchall()

    def insert_awards(self, awards):
        stmt = insert(Awards).on_conflict_do_nothing()
        self.session.execute(stmt, awards)
        self.session.commit()

    def collect_hofs_and_retires(self):
        print('collecting teams HOFs and retired jerseis')
        team_ids = self.get_teams_ids_and_last_name()
        if len(team_ids) == 0:
            return
        to_iterate = alive_it(team_ids, force_tty=True, title=f'Fetching Teams HOFs', enrich_print=False, dual_line=True)
        for (tid, t_name) in to_iterate:
            to_iterate.text(f'-> Fetching {t_name} hofs...')
            handler = TeamDetailsHandler(tid)
            data = call_with_retry(handler.downloader, 2)
            if not data:
                print(f'could not fetch {t_name} honors. try again later.')
                continue
            data = data['resultSets']
            hof_data = data[6]['rowSet']
            retired_data = data[7]['rowSet']
            hof_awards = [[p[0] if p[0] else 0,
                           p[1],
                           '#',
                           '#',
                           0,
                           None,
                           'Hall of Fame Inductee',
                           None,
                           p[5] if p[5] else 0,
                           datetime.min.date(),
                           None, 'Award', 'Hall of Fame', None, None] for p in hof_data]
            retired_honors = [[p[0] if p[0] else 0,
                               p[1],
                               p[3] if p[3] else '#',
                               p[2] if p[2] else '#',
                               tid,
                               None,
                               'Retired Jersey',
                               None,
                               p[5] if p[5] else 0,
                               datetime.min.date(),
                               None, 'Honor', 'Retired Jersey', None, None] for p in retired_data]
            to_insert = hof_awards + retired_honors
            to_insert = [dict(zip(self.awards_headers, award)) for award in to_insert]
            if to_insert:
                self.insert_awards(to_insert)
            time.sleep(STATS_DELAY_SECONDS)  # sleep to prevent ban

    def collect_players_awards(self, players_to_collect):
        def transform_award(award_row):
            full_name = award_row[1] + ' ' + award_row[2]
            season = int(award_row[6].split('-')[0]) if award_row[6] else 0
            team_id = [t[0] for t in self.teams_spans if t[2] == award_row[3] and t[3] <= season <= t[4]] if award_row[3] else 0
            if award_row[3]:
                if len(team_id) == 0:
                    # print(f'****************************************{award_row[3]} - {season}******************************')
                    team_id = award_row[3]
                else:
                    team_id = team_id[0]
            date_awarded = datetime.strptime(award_row[7], '%m/%d/%Y').date() if award_row[7] else (datetime.fromisoformat(award_row[8]).date() if award_row[8] else datetime.min.date())
            to_ret = [
                award_row[0],
                full_name,
                '#',
                '#',
                team_id,
                award_row[3],
                award_row[4] if award_row[4] else '',
                int(award_row[5]) if award_row[5] and award_row[5] != '(null)' else None,
                season,
                date_awarded,
                award_row[9], award_row[10], award_row[11], award_row[12], award_row[13]]
            return dict(zip(self.awards_headers, to_ret))
        if len(players_to_collect) == 0:
            return
        to_iterate = alive_it(players_to_collect, force_tty=True, title=f'Fetching Players Awards', enrich_print=False, dual_line=True)
        for (pid, p_name) in to_iterate:
            to_iterate.text(f'-> Fetching {p_name} Awards...')
            handler = PlayerAwardsHandler(pid)
            data = call_with_retry(handler.downloader, 2)
            if not data:
                print(f'couldnt fetch {p_name}({pid}) awards. try again later')
                continue
            data = data['resultSets'][0]['rowSet']
            awards = [transform_award(p) for p in data]
            if awards:
                self.insert_awards(awards)
            time.sleep(STATS_DELAY_SECONDS)  # sleep to prevent ban

    def collect_all_awards(self):
        print('collecting all Players awards')
        player_ids = self.get_players_ids_and_names()
        player_ids = player_ids
        self.collect_players_awards(player_ids)

    def collect_active_awards(self):
        print('collecting active Players awards')
        player_ids = self.get_active_players_ids_and_names()
        self.collect_players_awards(player_ids)

    def collect_player_awards(self, player_id):
        player_name = self.session.execute(select(Player.FullName).where(Player.PlayerId == player_id)).fetchall()
        if not player_name:
            print(f'could not find player with id {player_id}')
        player_name = player_name[0][0]
        print(f'collecting {player_name} Awards')
        self.collect_players_awards([(player_id, player_name)])
