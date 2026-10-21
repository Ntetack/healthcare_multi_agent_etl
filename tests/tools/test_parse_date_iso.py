"""ISO 8601 dates must never be read day-first.

An ISO 8601 date is written year first: `2021-04-07` is always the 7th of
April. The `dayfirst` flag of `parse_date` exists for ambiguous D/M/Y strings
(`03/04/2024`) and must have no effect on an ISO string.

The defect these tests guard against: a FHIR date carries a UTC offset
(`2021-04-07T10:33:05-04:00`), which no fast format of `parse_date` accepts.
It fell through to dateutil with `dayfirst=True`, which swaps day and month
whenever the day is 12 or less: April 7th became July 4th. About 40 % of the
dates of a FHIR export were affected, and none of the dates of a CSV export,
whose values end with `Z` or carry no time and use the fast formats.
"""
from __future__ import annotations

from datetime import date, datetime

import pytest

from app.tools.transformation.transform_tools import detect_day_first, parse_date


@pytest.mark.parametrize("dayfirst", [True, False])
def test_an_iso_datetime_with_an_offset_is_not_affected_by_dayfirst(dayfirst):
    parsed = parse_date("2021-04-07T10:33:05-04:00", dayfirst=dayfirst)
    assert (parsed.year, parsed.month, parsed.day) == (2021, 4, 7)


@pytest.mark.parametrize("dayfirst", [True, False])
def test_no_ambiguous_day_and_month_is_ever_swapped(dayfirst):
    for month in range(1, 13):
        for day in range(1, 13):
            parsed = parse_date(f"2020-{month:02d}-{day:02d}T12:00:00-05:00", dayfirst=dayfirst)
            assert (parsed.month, parsed.day) == (month, day), f"2020-{month:02d}-{day:02d}"


def test_an_offset_is_converted_to_utc_so_that_both_formats_agree():
    """The same instant written by a FHIR export (offset) and by a CSV export
    (Z, which is UTC) gives the same value."""
    fhir = parse_date("2021-04-07T10:33:05-04:00")
    csv = parse_date("2021-04-07T14:33:05Z")
    assert fhir == csv == datetime(2021, 4, 7, 14, 33, 5)


def test_an_evening_time_moves_to_the_next_utc_day_like_the_csv_export_does():
    assert parse_date("2021-04-07T21:10:00-04:00") == datetime(2021, 4, 8, 1, 10, 0)


@pytest.mark.parametrize("value", [
    "2021-04-07T10:33:05-04:00", "2021-04-07T10:33:05+05:30", "2021-04-07T10:33:05.123-04:00",
    "2021-04-07T10:33:05Z", "2021-04-07 10:33:05",
])
def test_the_result_never_carries_a_timezone(value):
    assert parse_date(value).tzinfo is None


@pytest.mark.parametrize("value, expected", [
    ("2021-04-07T14:33:05Z", datetime(2021, 4, 7, 14, 33, 5)),
    ("2021-04-07 14:33:05", datetime(2021, 4, 7, 14, 33, 5)),
    ("2021-04-07T14:33", datetime(2021, 4, 7, 14, 33)),
    ("2021-04-07", date(2021, 4, 7)),
    ("20210407", date(2021, 4, 7)),
])
def test_the_formats_that_already_worked_are_unchanged(value, expected):
    assert parse_date(value) == expected


@pytest.mark.parametrize("value, expected", [("2021-04", date(2021, 4, 1)), ("2021", date(2021, 1, 1))])
def test_a_partial_iso_date_is_still_completed_with_the_first_day(value, expected):
    """FHIR allows a date with only a year, or a year and a month."""
    assert parse_date(value, dayfirst=True) == expected
    assert parse_date(value, dayfirst=False) == expected


def test_an_ambiguous_slash_date_still_follows_the_flag():
    assert parse_date("03/04/2024", dayfirst=True) == date(2024, 4, 3)
    assert parse_date("03/04/2024", dayfirst=False) == date(2024, 3, 4)


def test_an_iso_only_column_is_harmless_whatever_detect_day_first_says():
    """detect_day_first looks for D/M/Y evidence and finds none in ISO values,
    so it answers True. That answer used to be applied to the ISO values."""
    column = ["2021-04-07T10:33:05-04:00", "2020-07-03T10:10:00-04:00"]    # daytime: the UTC date is the same
    flag = detect_day_first(column)
    swapped_free = [parse_date(v, dayfirst=flag) for v in column]
    assert [(d.month, d.day) for d in swapped_free] == [(4, 7), (7, 3)]


def test_an_unparseable_value_still_gives_none():
    assert parse_date("not a date") is None
    assert parse_date("") is None
    assert parse_date(None) is None
