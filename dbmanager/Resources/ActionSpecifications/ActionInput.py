import datetime
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ActionParameter:
    parameter_name: str
    parameter_type: str
    required: bool


@dataclass
class ActionInput(ABC):
    input_name: str = field(init=False)
    expected_params: List[ActionParameter] = field(init=False)


@dataclass
class SeasonTypeSelector(ActionInput):
    def __post_init__(self):
        self.input_name = 'SeasonTypeSelector'
        self.expected_params = [
            ActionParameter('season_type_code', 'str', True)
        ]


@dataclass
class DateRangeSelector(ActionInput):
    min_date: datetime.date
    max_date: datetime.date
    default_date: datetime.date

    def __post_init__(self):
        self.input_name = 'DateRangeSelector'
        self.expected_params = [
            ActionParameter('start_date', 'isodate', True),
            ActionParameter('end_date', 'isodate', True)
        ]


@dataclass
class SeasonRangeSelector(ActionInput):
    min_season: int
    max_season: int
    default_season: int
    excluded_seasons: List[int] = field(default_factory=lambda: [])

    def __post_init__(self):
        self.input_name = 'SeasonRangeSelector'
        self.expected_params = [
            ActionParameter('start_season', 'int', True),
            ActionParameter('end_season', 'int', True)
        ]


@dataclass
class FileSelector(ActionInput):
    example_file_link: Optional[str] = None

    def __post_init__(self):
        self.input_name = 'FileSelector'
        self.expected_params = [
            ActionParameter('file_path', 'str', True)
        ]


@dataclass
class PlayersAutoComplete(ActionInput):
    def __post_init__(self):
        self.input_name = 'PlayersAutoComplete'
        self.expected_params = [
            ActionParameter('player_id', 'int', True),
        ]


@dataclass
class TeamsAutoComplete(ActionInput):
    def __post_init__(self):
        self.input_name = 'TeamsAutoComplete'
        self.expected_params = [
            ActionParameter('team_id', 'int', True),
        ]


@dataclass
class AwardsSelector(ActionInput):
    def __post_init__(self):
        self.input_name = 'AwardsSelector'
        self.expected_params = [
            ActionParameter('award_id', 'str', True),
        ]
