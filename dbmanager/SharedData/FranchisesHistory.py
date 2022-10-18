import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

import requests

from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc
from dbmanager.constants import FRANCHISE_HISTORY_ENDPOINT, STATS_HEADERS


@dataclass
class FranchiseSpan:
    franchise_id: int
    franchise_name: str
    span_start_year: int
    span_end_year: int
    is_defunct: bool
    last_span: bool


class FranchisesHistory(SharedDataResourceAbc):
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

    def get_spans(self) -> List[FranchiseSpan]:
        return self.get_data()

    def get_spans_in_range(self, team_name: str, season: int) -> List[FranchiseSpan]:
        return [t for t in self.get_spans() if
                t.franchise_name == team_name and t.span_start_year <= season <= t.span_end_year]


franchises_history = FranchisesHistory()
