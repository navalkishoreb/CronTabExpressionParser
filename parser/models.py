from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from parser import CronTabExpressionParseError
from parser.config import DEFAULT_SEGMENT_TYPE_ORDER, DEFAULT_TITLE_FILL_WIDTH
from parser.transformers import (
    transform_cron_segment_text_to_applicable_list_of_values,
    transform_input_expression_into_segment_text,
)


@dataclass
class CronSegment:
    segment_text: str
    title: str

    def get_formatted_title(self):
        return f"{self.title:<{DEFAULT_TITLE_FILL_WIDTH}}"

    def __str__(self):
        return f"{self.get_formatted_title()}{self.segment_text}"


@dataclass
class CronScheduleSegment(CronSegment):
    segment_range_end: int
    segment_range_start: int
    segment_range: Optional[List[int]] = None
    applicable_values: Optional[List[int]] = None

    def __post_init__(self):
        assert self.segment_text, "Provide cron segment test"
        assert self.segment_range_start is not None, "Provide cron segment range start"
        assert self.segment_range_end is not None, "Provide cron segment range end"
        if not self.segment_range:
            self.segment_range = list(
                range(self.segment_range_start, self.segment_range_end + 1)
            )
        if not self.applicable_values:
            self.applicable_values = (
                transform_cron_segment_text_to_applicable_list_of_values(
                    self.segment_text, self.segment_range
                )
            )

    def get_formatted_applicable_times(self):
        return " ".join([str(item) for item in self.applicable_values])

    def __str__(self):
        return f"{self.get_formatted_title()}{self.get_formatted_applicable_times()}"


@dataclass
class MinuteCronSegment(CronScheduleSegment):
    title: str = field(default="minute")
    segment_range_start: int = field(default=0)
    segment_range_end: int = field(default=59)


@dataclass
class HourCronSegment(CronScheduleSegment):
    title: str = field(default="hour")
    segment_range_start: int = field(default=0)
    segment_range_end: int = field(default=23)


@dataclass
class DayOfTheMonthCronSegment(CronScheduleSegment):
    title: str = field(default="day of month")
    segment_range_start: int = field(default=1)
    segment_range_end: int = field(default=31)


@dataclass
class MonthCronSegment(CronScheduleSegment):
    title: str = field(default="month")
    segment_range_start: int = field(default=1)
    segment_range_end: int = field(default=12)


@dataclass
class DayOfTheWeekCronSegment(CronScheduleSegment):
    title: str = field(default="day of week")
    segment_range_start: int = field(default=0)
    segment_range_end: int = field(default=6)


@dataclass
class CommandCronSegment(CronSegment):
    title: str = field(default="command")


class CronSegmentType(Enum):
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY_OF_THE_MONTH = "DAY_OF_THE_MONTH"
    MONTH = "MONTH"
    DAY_OF_THE_WEEK = "DAY_OF_THE_WEEK"
    COMMAND = "COMMAND"


def get_cron_segment(segment_type, segment_text) -> CronSegment:
    if segment_type == CronSegmentType.MINUTE.value:
        return MinuteCronSegment(segment_text=segment_text)
    elif segment_type == CronSegmentType.HOUR.value:
        return HourCronSegment(segment_text=segment_text)
    elif segment_type == CronSegmentType.DAY_OF_THE_MONTH.value:
        return DayOfTheMonthCronSegment(segment_text=segment_text)
    elif segment_type == CronSegmentType.MONTH.value:
        return MonthCronSegment(segment_text=segment_text)
    elif segment_type == CronSegmentType.DAY_OF_THE_WEEK.value:
        return DayOfTheWeekCronSegment(segment_text=segment_text)
    elif segment_type == CronSegmentType.COMMAND.value:
        return CommandCronSegment(segment_text=segment_text)
    else:
        raise CronTabExpressionParseError(
            f"Not implemented segment type {segment_type !r} "
        )


def transform_input_segments_to_cron_segments(
    segments: List[str], segment_order: List[str]
):
    cron_segments = []
    for segment_type, segment_text in zip(segment_order, segments):
        cron_segment = get_cron_segment(
            segment_type=segment_type, segment_text=segment_text
        )
        cron_segments.append(cron_segment)
    return cron_segments


def transform_cron_expression(expression: str) -> List[CronSegment]:
    segments = transform_input_expression_into_segment_text(expression=expression)
    cron_segments = transform_input_segments_to_cron_segments(
        segments=segments, segment_order=DEFAULT_SEGMENT_TYPE_ORDER
    )

    return cron_segments


@dataclass
class CronJob:
    expression: str
    cron_segments: List[CronSegment] = None

    def __post_init__(self):
        if not self.expression:
            raise CronTabExpressionParseError("Provide cron job expression")
        if not self.cron_segments:
            self.cron_segments = transform_cron_expression(expression=self.expression)

    def __str__(self):
        return "\n".join([str(item) for item in self.cron_segments])
