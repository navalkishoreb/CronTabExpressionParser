from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from parser import CronTabExpressionParseError
from parser.config import DEFAULT_TITLE_FILL_WIDTH


@dataclass
class CronSegment:
    title: str

    def get_formatted_title(self):
        return f"{self.title:<{DEFAULT_TITLE_FILL_WIDTH}}"


@dataclass
class ScheduleCronSegment(CronSegment):
    applicable_values: List[int]

    def get_formatted_applicable_times(self):
        return " ".join([str(item) for item in self.applicable_values])

    def __str__(self):
        return f"{self.get_formatted_title()}{self.get_formatted_applicable_times()}"


@dataclass
class CommandCronSegment(CronSegment):
    command: str

    def __str__(self):
        return f"{self.get_formatted_title()}{self.command}"


class CronSegmentType(Enum):
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY_OF_THE_MONTH = "DAY_OF_THE_MONTH"
    MONTH = "MONTH"
    DAY_OF_THE_WEEK = "DAY_OF_THE_WEEK"
    COMMAND = "COMMAND"


@dataclass
class SegmentParams:
    title: str
    has_range: bool
    start: Optional[int] = None
    end: Optional[int] = None

    def __post_init__(self):
        if (
            self.has_range
            and (self.start is not None or self.end is not None)
            and (self.start > self.end)
        ):
            raise CronTabExpressionParseError(
                f"Provide proper start {self.start !r} and end {self.end !r} range"
            )

    def get_segment_range(self):
        return list(range(self.start, self.end + 1))


@dataclass
class CronJob:
    cron_segments: List[CronSegment] = None

    def __str__(self):
        return "\n".join([str(item) for item in self.cron_segments])
