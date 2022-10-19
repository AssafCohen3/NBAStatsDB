import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc
from dbmanager.constants import FRANCHISE_HISTORY_ENDPOINT, STATS_HEADERS


@dataclass(unsafe_hash=True)
class FranchiseSpan:
    franchise_id: int
    franchise_name: str
    span_start_year: int
    span_end_year: int
    is_defunct: bool
    last_span: bool


class FranchisesHistory(SharedDataResourceAbc[List[FranchiseSpan]]):
    def _fetch_data(self):
        resp = requests.get(FRANCHISE_HISTORY_ENDPOINT, headers=STATS_HEADERS)
        resp = json.loads(resp.text)
        active_franchises = resp['resultSets'][0]['rowSet']
        defunct_franchises = resp['resultSets'][1]['rowSet']
        active_franchises = [(row, False) for row in active_franchises]
        defunct_franchises = [(row, True) for row in defunct_franchises]
        to_iterate = [*active_franchises, *defunct_franchises]
        grouped: Dict[int, List[FranchiseSpan]] = defaultdict(list)
        to_ret: List[FranchiseSpan] = []
        for franchise, is_defunct in to_iterate:
            franchise_name = franchise[2] + ' ' + franchise[3]
            start_year = int(franchise[4])
            end_year = int(franchise[5])
            to_add = FranchiseSpan(franchise[1], franchise_name, start_year, end_year, is_defunct, False)
            grouped[franchise[1]].append(to_add)
        for franchise_id, spans in grouped.items():
            to_append = spans
            if len(spans) > 1:
                to_append = spans[1:]
            to_append[0].last_span = True
            to_ret.extend(to_append)
        return to_ret

    def get_spans_in_range(self, team_name: str, season: int) -> List[FranchiseSpan]:
        return [t for t in self.get_data() if
                t.franchise_name == team_name and t.span_start_year <= season <= t.span_end_year]

    def search_franchise(self, search: str, limit: int = 10) -> List[FranchiseSpan]:
        to_ret = [s for s in self.get_data() if search.lower() in s.franchise_name.lower()]
        to_ret = list(set(self.get_last_span_with_id(s.franchise_id) for s in to_ret))[:limit]
        return to_ret

    def get_last_span_with_id(self, team_id: int) -> Optional[FranchiseSpan]:
        to_ret = [s for s in self.get_data() if s.franchise_id == team_id and s.last_span]
        return to_ret[0] if to_ret else None

    def get_franchises(self):
        return [s for s in self.get_data() if s.last_span]


franchises_history = FranchisesHistory()
