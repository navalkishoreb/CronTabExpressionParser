import pytest

from parser import CronTabExpressionParseError
from parser.models import SegmentParams


@pytest.mark.parametrize(
    argnames=["start", "end", "expected"],
    argvalues=[
        [
            None,
            None,
            CronTabExpressionParseError("Provide proper start None and end None range"),
        ],
        [
            2,
            1,
            CronTabExpressionParseError("Range start 2 is greater then end 1 "),
        ],
    ],
)
def test_segment_params_raise_error(start, end, expected):
    with pytest.raises(CronTabExpressionParseError) as actual:
        _ = SegmentParams(title="minute", has_range=True, start=start, end=end)
    assert actual.value.args == expected.args
