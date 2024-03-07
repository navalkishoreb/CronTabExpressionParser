from typing import List

from parser import CronTabExpressionParseError
from parser.config import (
    DEFAULT_DELIMITER,
    DEFAULT_CRON_SEGMENTS_COUNT,
    DEFAULT_STEP_DELIMITER,
    DEFAULT_LIST_DELIMITER,
    DEFAULT_RANGE_DELIMITER,
    DEFAULT_ALL_SELECTOR,
    DEFAULT_SEGMENT_TYPE_ORDER,
    DEFAULT_SEGMENT_TYPE_PARAMETERS,
)
from parser.models import (
    CronSegment,
    CronJob,
    CommandCronSegment,
    SegmentParams,
    ScheduleCronSegment,
)


def parse_single_integer(segment_text: str, segment_range: List[int]) -> List[int]:
    if segment_text is None:
        raise CronTabExpressionParseError("Received None segment text. Expected digits")
    if not segment_text:
        raise CronTabExpressionParseError(
            f"Received empty segment text. Expected digits"
        )
    try:
        single_integer = int(segment_text)
        if single_integer in segment_range:
            return [single_integer]
        else:
            raise CronTabExpressionParseError(
                f"Expected value {single_integer!r} in segment range {segment_range!r}"
            )
    except ValueError:
        raise CronTabExpressionParseError(
            f"Expected integer in segment text {segment_text !r}"
        )


def parse_range_segment(
    segment_text: str,
    segment_range: List[int],
    delimiter: str = DEFAULT_RANGE_DELIMITER,
) -> List[int]:
    if delimiter not in segment_text:
        raise CronTabExpressionParseError(
            f"Expected delimiter {delimiter !r} in {segment_text !r}"
        )
    split_segment_text = None
    try:
        split_segment_text = segment_text.split(delimiter, maxsplit=1)
        start_range, end_range = list(map(int, split_segment_text))
        if start_range > end_range:
            raise CronTabExpressionParseError(
                f"Range segment text in improper order start range {start_range !r} and end range {end_range !r}"
            )
        selected_values = [
            item for item in segment_range if start_range <= item <= end_range
        ]
        return sorted(selected_values)
    except ValueError:
        raise CronTabExpressionParseError(
            f"Expected integer in segment text {split_segment_text !r}"
        )


def parse_list_segment(
    segment_text: str,
    segment_range: List[int],
    delimiter: str = DEFAULT_LIST_DELIMITER,
) -> List[int]:
    if delimiter not in segment_text:
        raise CronTabExpressionParseError(
            f"Expected delimiter {delimiter !r} in {segment_text !r}"
        )
    list_segment = segment_text.split(delimiter)
    selected_values = []
    for list_segment_item in list_segment:
        if DEFAULT_RANGE_DELIMITER in list_segment_item:
            result = parse_range_segment(
                segment_text=list_segment_item, segment_range=segment_range
            )
        else:
            result = parse_single_integer(
                segment_text=list_segment_item, segment_range=segment_range
            )
        selected_values.extend(result)

    return sorted(selected_values)


def parse_step_segment(
    segment_text: str,
    segment_range: List[int],
    delimiter: str = DEFAULT_STEP_DELIMITER,
) -> List[int]:
    if delimiter not in segment_text:
        raise CronTabExpressionParseError(
            f"Expected delimiter {delimiter !r} in {segment_text !r}"
        )
    remaining_segment_text, step_string = segment_text.split(
        DEFAULT_STEP_DELIMITER, maxsplit=1
    )
    try:
        step = int(step_string)
    except ValueError:
        raise CronTabExpressionParseError(
            f"Received malformed step value {step_string !r}"
        )
    segment_range = [item for item in segment_range if item % step == 0]
    return transform_segment_text_to_applicable_values(
        segment_text=remaining_segment_text, segment_range=segment_range
    )


def transform_segment_text_to_applicable_values(
    segment_text: str, segment_range: List[int]
) -> List[int]:
    if not segment_text:
        raise CronTabExpressionParseError("Provide segment text")
    if segment_range is None:
        raise CronTabExpressionParseError(f"Provide segment range")

    if DEFAULT_STEP_DELIMITER in segment_text:
        return parse_step_segment(
            segment_text=segment_text, segment_range=segment_range
        )

    elif DEFAULT_LIST_DELIMITER in segment_text:
        return parse_list_segment(
            segment_text=segment_text, segment_range=segment_range
        )

    elif DEFAULT_RANGE_DELIMITER in segment_text:
        return parse_range_segment(
            segment_text=segment_text, segment_range=segment_range
        )

    elif DEFAULT_ALL_SELECTOR in segment_text:
        return segment_range

    else:
        return parse_single_integer(
            segment_text=segment_text, segment_range=segment_range
        )


def transform_input_expression_into_segment_text(
    expression: str,
    delimiter=DEFAULT_DELIMITER,
    cron_segments_count_limit=DEFAULT_CRON_SEGMENTS_COUNT,
) -> List[str]:
    if expression is None:
        raise CronTabExpressionParseError("Provided expression is None")

    #  strip whitespaces at start and end of the input string
    expression = expression.strip()
    if not expression:
        raise CronTabExpressionParseError(f"Provide expression is empty")

    segments = expression.split(sep=delimiter, maxsplit=cron_segments_count_limit - 1)
    if len(segments) != cron_segments_count_limit:
        raise CronTabExpressionParseError(
            f"Received {len(segments)} segments, expected {cron_segments_count_limit}.\n{segments =!r}"
        )

    return segments


def transform_input_segments_to_cron_segments(
    segments: List[str], segment_order: List[str]
):
    cron_segments = []
    for segment_type, segment_text in zip(segment_order, segments):
        cron_segment = transform_segment_text_to_cron_segment(
            segment_type=segment_type, segment_text=segment_text
        )
        cron_segments.append(cron_segment)
    return cron_segments


def transform_cron_expression_to_cron_job(expression: str) -> CronJob:
    segments = transform_input_expression_into_segment_text(expression=expression)
    cron_segments = transform_input_segments_to_cron_segments(
        segments=segments, segment_order=DEFAULT_SEGMENT_TYPE_ORDER
    )

    return CronJob(cron_segments=cron_segments)


def transform_segment_text_to_cron_segment(segment_type, segment_text) -> CronSegment:
    segment_params = DEFAULT_SEGMENT_TYPE_PARAMETERS.get(segment_type, None)
    if not segment_params:
        raise CronTabExpressionParseError(
            f"Segment type {segment_type !r} not implemented"
        )

    params = SegmentParams(**segment_params)
    if params.has_range:
        applicable_values = transform_segment_text_to_applicable_values(
            segment_text=segment_text, segment_range=params.get_segment_range()
        )
        return ScheduleCronSegment(
            applicable_values=applicable_values, title=params.title
        )
    else:
        return CommandCronSegment(title=params.title, command=segment_text)
