import datetime
from abc import ABC
from dataclasses import dataclass, field
from typing import List


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
            ActionParameter('season_type_code', 'int', True)
        ]


@dataclass
class DateRangeSelector(ActionInput):
    # TODO how send this as string
    min_date: datetime.date
    max_date: datetime.date
    default_date: datetime.date

    def __post_init__(self):
        self.input_name = 'DateRangeSelector'
        self.expected_params = [
            ActionParameter('start_date', 'isodate', True),
            ActionParameter('end_date', 'isodate', True)
        ]
