from dataclasses import dataclass
from typing import List


@dataclass
class SeasonType:
    code: str
    name: str
    api_name: str


SEASON_TYPES = [
    SeasonType('2', 'Regular Season', 'Regular+Season'),
    SeasonType('3', 'All Star', 'All+Star'),
    SeasonType('4', 'Playoffs', 'Playoffs'),
    SeasonType('5', 'PlayIn', 'PlayIn')
]


def get_season_types(season_type_code: str) -> List[SeasonType]:
    """
    get season types by code
    :param season_type_code: the season type code. 0 for all
    :return: season types according to the code
    """
    return [season_type for season_type in SEASON_TYPES if season_type.code == season_type_code or season_type_code == '0']

