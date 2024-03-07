import pytest

from parser import CronTabExpressionParseError
from parser.transformers import (
    transform_input_expression_into_segment_text,
    transform_segment_text_to_applicable_values,
    parse_single_integer,
    parse_range_segment,
    parse_list_segment,
    transform_cron_expression_to_cron_job,
    parse_step_segment,
    transform_segment_text_to_cron_segment,
)


@pytest.mark.parametrize(
    argnames=["input_string", "expected_string"],
    argvalues=[
        [
            "0 */2 * * * /bin/bash collect_metrics.sh",
            ["0", "*/2", "*", "*", "*", "/bin/bash collect_metrics.sh"],
        ],
        [
            "    0 */2 * * * /bin/bash collect_metrics.sh",
            ["0", "*/2", "*", "*", "*", "/bin/bash collect_metrics.sh"],
        ],
    ],
)
def test_transform_input_expression_into_segment_text(input_string, expected_string):
    actual = transform_input_expression_into_segment_text(input_string)
    assert actual == expected_string


@pytest.mark.parametrize(
    argnames=["input_string", "expected_error"],
    argvalues=[
        [
            None,
            CronTabExpressionParseError("Provided expression is None"),
        ],
        [
            "",
            CronTabExpressionParseError("Provide expression is empty"),
        ],
        [
            "0 */2 * * *",
            CronTabExpressionParseError(
                "Received 5 segments, expected 6.\nsegments =['0', '*/2', '*', '*', '*']"
            ),
        ],
    ],
)
def test_transform_input_expression_into_segment_text_raise_error(
    input_string, expected_error
):
    with pytest.raises(CronTabExpressionParseError) as exec_info:
        _ = transform_input_expression_into_segment_text(input_string)
    assert isinstance(exec_info.value, CronTabExpressionParseError)
    assert exec_info.value.args == expected_error.args


@pytest.mark.parametrize(
    argnames=[
        "segment_text",
        "segment_range",
        "expected",
    ],
    argvalues=[
        ["1", [0, 1, 2], [1]],
    ],
)
def test_select_single_integer(segment_text, segment_range, expected):
    actual = parse_single_integer(
        segment_text=segment_text, segment_range=segment_range
    )
    assert actual == expected


@pytest.mark.parametrize(
    argnames=[
        "segment_text",
        "segment_range",
        "expected",
    ],
    argvalues=[
        [
            "1",
            [7, 8, 9],
            CronTabExpressionParseError("Expected value 1 in segment range [7, 8, 9]"),
        ],
        [
            "1l",
            [0, 1, 2],
            CronTabExpressionParseError("Expected integer in segment text '1l'"),
        ],
        [
            "",
            [0, 1, 2],
            CronTabExpressionParseError("Received empty segment text. Expected digits"),
        ],
        [
            None,
            [0, 1, 2],
            CronTabExpressionParseError("Received None segment text. Expected digits"),
        ],
    ],
)
def test_select_single_integer_raises_error(segment_text, segment_range, expected):
    with pytest.raises(CronTabExpressionParseError) as exec_info:
        _ = parse_single_integer(segment_text=segment_text, segment_range=segment_range)
    assert isinstance(exec_info.value, CronTabExpressionParseError)
    assert exec_info.value.args == expected.args


@pytest.mark.parametrize(
    argnames=[
        "segment_text",
        "segment_range",
        "expected",
    ],
    argvalues=[
        [
            "*2",
            [7, 8, 9],
            CronTabExpressionParseError("Expected delimiter '/' in '*2'"),
        ],
        [
            "*/a",
            [0, 1, 2],
            CronTabExpressionParseError("Received malformed step value 'a'"),
        ],
    ],
)
def test_parse_step_segment_raises_error(segment_text, segment_range, expected):
    with pytest.raises(CronTabExpressionParseError) as exec_info:
        _ = parse_step_segment(segment_text=segment_text, segment_range=segment_range)
    assert isinstance(exec_info.value, CronTabExpressionParseError)
    assert exec_info.value.args == expected.args


@pytest.mark.parametrize(
    argnames=[
        "segment_text",
        "segment_range",
        "expected",
    ],
    argvalues=[
        ["1-5", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5]],
    ],
)
def test_parse_range_segment(segment_text, segment_range, expected):
    actual = parse_range_segment(segment_text=segment_text, segment_range=segment_range)
    assert actual == expected


@pytest.mark.parametrize(
    argnames=[
        "segment_text",
        "segment_range",
        "expected",
    ],
    argvalues=[
        [
            "1)5",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            CronTabExpressionParseError("Expected delimiter '-' in '1)5'"),
        ],
        [
            "1--5",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            CronTabExpressionParseError(
                "Range segment text in improper order start range 1 and end range -5",
            ),
        ],
        [
            "5-1",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            CronTabExpressionParseError(
                "Range segment text in improper order start range 5 and end range 1",
            ),
        ],
        [
            "1---5",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            CronTabExpressionParseError(
                "Expected integer in segment text ['1', '--5']",
            ),
        ],
    ],
)
def test_parse_range_segment_raises_error(segment_text, segment_range, expected):
    with pytest.raises(CronTabExpressionParseError) as exec_info:
        _ = parse_range_segment(segment_text=segment_text, segment_range=segment_range)
    assert isinstance(exec_info.value, CronTabExpressionParseError)
    assert exec_info.value.args == expected.args


@pytest.mark.parametrize(
    argnames=[
        "segment_text",
        "segment_range",
        "expected",
    ],
    argvalues=[
        ["1,5", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 5]],
        ["1-3,5", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 5]],
        ["1-3,5-7", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 5, 6, 7]],
        ["5-7,1-3", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 5, 6, 7]],
    ],
)
def test_parse_list_segment(segment_text, segment_range, expected):
    actual = parse_list_segment(segment_text=segment_text, segment_range=segment_range)
    assert actual == expected


@pytest.mark.parametrize(
    argnames=[
        "segment_text",
        "segment_range",
        "expected",
    ],
    argvalues=[
        [
            "1)5",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            CronTabExpressionParseError("Expected delimiter ',' in '1)5'"),
        ],
        [
            "1,,5",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            CronTabExpressionParseError(
                "Received empty segment text. Expected digits",
            ),
        ],
        [
            "13,14",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            CronTabExpressionParseError(
                "Expected value 13 in segment range [0, 1, 2, 3, 4, 5, 6, 7, 8, "
                "9, 10]",
            ),
        ],
    ],
)
def test_parse_list_segment_raises_error(segment_text, segment_range, expected):
    with pytest.raises(CronTabExpressionParseError) as exec_info:
        _ = parse_list_segment(segment_text=segment_text, segment_range=segment_range)
    assert isinstance(exec_info.value, CronTabExpressionParseError)
    assert exec_info.value.args == expected.args


@pytest.mark.parametrize(
    argnames=["segment_text", "segment_range", "expected"],
    argvalues=[
        ["*/2", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [0, 2, 4, 6, 8, 10]],
        ["1,7,8", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 7, 8]],
        ["1-5", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5]],
        ["1-5,7-8/4", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [4, 8]],
    ],
)
def test_transform_cron_segment_text_to_applicable_list_of_values(
    segment_text, segment_range, expected
):
    actual = transform_segment_text_to_applicable_values(
        segment_text=segment_text, segment_range=segment_range
    )
    assert actual == expected


@pytest.mark.parametrize(
    argnames=["segment_text", "segment_range", "expected"],
    argvalues=[
        ["1", [], CronTabExpressionParseError("Expected value 1 in segment range []")],
        ["", [], CronTabExpressionParseError("Provide segment text")],
        ["", [1], CronTabExpressionParseError("Provide segment text")],
        ["1", None, CronTabExpressionParseError("Provide segment range")],
    ],
)
def test_transform_segment_text_to_applicable_values_raise_error(
    segment_text, segment_range, expected
):
    with pytest.raises(CronTabExpressionParseError) as actual:
        transform_segment_text_to_applicable_values(
            segment_text=segment_text, segment_range=segment_range
        )

    assert actual.value.args == expected.args


@pytest.mark.parametrize(
    argnames=["segment_type", "segment_text", "expected"],
    argvalues=[
        ["", "1", CronTabExpressionParseError("Segment type '' not implemented")],
        [None, "1", CronTabExpressionParseError("Segment type None not implemented")],
    ],
)
def test_transform_segment_text_to_cron_segment_raise_error(
    segment_type, segment_text, expected
):
    with pytest.raises(CronTabExpressionParseError) as actual:
        transform_segment_text_to_cron_segment(
            segment_type=segment_type, segment_text=segment_text
        )

    assert actual.value.args == expected.args


@pytest.mark.parametrize(
    argnames=["expression", "expected"],
    argvalues=[
        [
            "*/15 0 1,15 * 1-5 /usr/bin/find",
            (
                "minute        0 15 30 45\n"
                "hour          0\n"
                "day of month  1 15\n"
                "month         1 2 3 4 5 6 7 8 9 10 11 12\n"
                "day of week   1 2 3 4 5\n"
                "command       /usr/bin/find"
            ),
        ],
        [
            "*/2 */2 */2 */2 */2 /bin/bash collect_metrics.sh",
            (
                "minute        0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 36 38 40 42 "
                "44 46 48 50 52 54 56 58\n"
                "hour          0 2 4 6 8 10 12 14 16 18 20 22\n"
                "day of month  2 4 6 8 10 12 14 16 18 20 22 24 26 28 30\n"
                "month         2 4 6 8 10 12\n"
                "day of week   0 2 4 6\n"
                "command       /bin/bash collect_metrics.sh"
            ),
        ],
    ],
)
def test_cron_job(expression, expected):
    actual = transform_cron_expression_to_cron_job(expression=expression)
    assert str(actual) == expected


@pytest.mark.parametrize(
    argnames=["expression", "expected"],
    argvalues=[
        [
            "*/15 /usr/bin/find",
            CronTabExpressionParseError(
                "Received 2 segments, expected 6.\nsegments =['*/15', '/usr/bin/find']"
            ),
        ],
        [
            "*/61 */2 */2 */2 */2 /bin/bash collect_metrics.sh",
            CronTabExpressionParseError("Step value 61 is out of bounds"),
        ],
        [
            "*/0 */2 */2 */2 */2 /bin/bash collect_metrics.sh",
            CronTabExpressionParseError("Step value cannot be zero"),
        ],
    ],
)
def test_cron_job_raise_error(expression, expected):
    with pytest.raises(CronTabExpressionParseError) as actual:
        _ = transform_cron_expression_to_cron_job(expression=expression)
    assert actual.value.args == expected.args
