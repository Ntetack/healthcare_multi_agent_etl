"""Real hospital exports mix date formats (Y-M-D, D-M-Y, D/M/Y, Y/M/D)
and some carry a time component (H:M:S) while others don't - all must
be handled without silently dropping the time or crashing."""
import datetime as dt

from app.tools.transformation.transform_tools import parse_date


def test_various_date_only_formats():
    assert parse_date("2024-01-15") == dt.date(2024, 1, 15)
    assert parse_date("2024/01/15") == dt.date(2024, 1, 15)
    assert parse_date("15/01/2024") == dt.date(2024, 1, 15)  # D/M/Y
    assert parse_date("15-01-2024") == dt.date(2024, 1, 15)  # D-M-Y
    assert parse_date("20240115") == dt.date(2024, 1, 15)    # compact


def test_datetime_with_seconds_not_dropped():
    result = parse_date("2024-01-15 14:30:45")
    assert result == dt.datetime(2024, 1, 15, 14, 30, 45)
    assert result.hour == 14 and result.minute == 30 and result.second == 45


def test_datetime_iso_t_separator():
    result = parse_date("2024-01-15T14:30:45")
    assert result == dt.datetime(2024, 1, 15, 14, 30, 45)


def test_datetime_without_seconds():
    result = parse_date("2024-01-15 14:30")
    assert result == dt.datetime(2024, 1, 15, 14, 30)


def test_unparseable_value_returns_none_not_crash():
    assert parse_date("not a date at all") is None
    assert parse_date("") is None
    assert parse_date(None) is None
