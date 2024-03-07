DEFAULT_DELIMITER = " "
DEFAULT_CRON_SEGMENTS_COUNT = 6
DEFAULT_LIST_DELIMITER = ","
DEFAULT_RANGE_DELIMITER = "-"
DEFAULT_ALL_SELECTOR = "*"
DEFAULT_STEP_DELIMITER = "/"
DEFAULT_SEGMENT_TYPE_ORDER = [
    "MINUTE",
    "HOUR",
    "DAY_OF_THE_MONTH",
    "MONTH",
    "DAY_OF_THE_WEEK",
    "COMMAND",
]
DEFAULT_TITLE_FILL_WIDTH = 14
DEFAULT_SEGMENT_TYPE_PARAMETERS = {
    "MINUTE": {"title": "minute", "start": 0, "end": 59, "has_range": True},
    "HOUR": {"title": "hour", "start": 0, "end": 23, "has_range": True},
    "DAY_OF_THE_MONTH": {
        "title": "day of month",
        "start": 1,
        "end": 31,
        "has_range": True,
    },
    "MONTH": {"title": "month", "start": 1, "end": 12, "has_range": True},
    "DAY_OF_THE_WEEK": {
        "title": "day of week",
        "start": 0,
        "end": 6,
        "has_range": True,
    },
    "COMMAND": {"title": "command", "has_range": False},
}
