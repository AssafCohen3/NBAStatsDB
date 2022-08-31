import time
from dbmanager.MainRequestsSession import call_with_retry
from datetime import datetime
from alive_progress import alive_it
from sqlalchemy import func
from sqlalchemy.sql import select
from dbmanager.Database.Models.Awards import Awards
from dbmanager.Database.Models.BoxScoreT import BoxScoreT
from dbmanager.Downloaders.TeamDetailsHandler import TeamDetailsHandler
from dbmanager.Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert
from dbmanager.constants import STATS_DELAY_SECONDS


class HonoursResourceHandler(ResourceAbc):

    def __init__(self, session):
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
        super().__init__(session)

    def get_teams_ids_and_last_name(self):
        stmt = select(BoxScoreT.TeamId, func.first_value(BoxScoreT.TeamName)
                      .over(partition_by=[BoxScoreT.TeamId],
                            order_by=[BoxScoreT.GameDate.desc()])).distinct()
        return self.session.execute(stmt).fetchall()

    def insert_awards(self, awards):
        if not awards:
            return
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
