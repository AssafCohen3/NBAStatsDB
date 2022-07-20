from pbpstats.data_loader.stats_nba.enhanced_pbp.loader import StatsNbaEnhancedPbpLoader
from pbpstats.resources.enhanced_pbp.stats_nba.enhanced_pbp_factory import StatsNbaEnhancedPbpFactory
# from pbpstats.data_loader.data_nba.pbp.loader import DataNbaPbpLoader
# from pbpstats.data_loader.data_nba.pbp.web import DataNbaPbpWebLoader
#
# from requests import HTTPError
#
from dbmanager.pbp.MySourceLoader import MySourceLoader


class MyPBPLoader(StatsNbaEnhancedPbpLoader):
    def __init__(self, game_id, events):
        self.file_directory = None
        self.shots_source_loader = None
        super().__init__(game_id, MySourceLoader(None, events))

    def _make_pbp_items(self):
        self._fix_order_when_technical_foul_before_period_start()
        self.factory = StatsNbaEnhancedPbpFactory()
        self.items = [
            self.factory.get_event_class(item["EVENTMSGTYPE"])(item, i)
            for i, item in enumerate(self.data)
        ]
        self._add_extra_attrs_to_all_events()
        self._check_rebound_event_order(6)

    def _use_data_nba_event_order(self):
        return
        # """
        # reorders all events to be the same order as data.nba.com pbp
        # """
        # # Order event numbers of events in data.nba.com pbp
        # if self is not None or False:
        #     return
        # try:
        #     data_nba_pbp = DataNbaPbpLoader(self.game_id, DataNbaPbpWebLoader())
        # except HTTPError as e:
        #     if e.response.status_code == 404:
        #         return
        #     raise e
        # data_nba_event_num_order = [item.evt for item in data_nba_pbp.items]
        #
        # headers = self.source_data["resultSets"][0]["headers"]
        # rows = self.source_data["resultSets"][0]["rowSet"]
        # event_num_index = headers.index("EVENTNUM")
        #
        # # reorder stats.nba.com events to be in same order as data.nba.com events
        # new_event_order = []
        # for event_num in data_nba_event_num_order:
        #     for row in rows:
        #         if row[event_num_index] == event_num:
        #             new_event_order.append(row)
        # self.source_data["resultSets"][0]["rowSet"] = new_event_order
        # self._save_data_to_file()
