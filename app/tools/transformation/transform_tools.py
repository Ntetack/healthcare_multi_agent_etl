"""
Transformation tools. The Transformation Agent decides *which* of these
to apply to which field (its "Transformation Plan"); the tools themselves
are pure, deterministic, and source-agnostic - they know nothing about
MIMIC/Synthea/hospital_a specifically.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

import re

import dateutil.parser

# Datetime formats (with time) tried FIRST - a value with a time
# component must not be silently truncated to a bare date by matching a
# date-only format that happens to parse just the date portion. Only
# UNAMBIGUOUS formats belong here (year always first, 4 digits) -
# slash/dash D-M-Y or M-D-Y style formats are ambiguous and must go
# through the dayfirst-aware fallback below instead, never guessed by
# a fixed try-order.
_DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO8601 UTC/Zulu (e.g. Synthea exports)
    "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d %H:%M:%S",
    "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M",
]

_DATE_FORMATS = [
    "%Y-%m-%d", "%Y/%m/%d", "%Y%m%d",
]

# A value with no time component gets midnight by convention when
# checking dateutil's fallback - the standard, unsurprising default for
# "no time specified" (matches how most systems treat a bare date).
_MIDNIGHT = datetime(2000, 1, 1, 0, 0, 0).time()

_AMBIGUOUS_DMY_PATTERN = re.compile(r"^(\d{1,2})[/-](\d{1,2})[/-]\d{2,4}")
_AMBIGUOUS_COMPACT_PATTERN = re.compile(r"^(\d{2})(\d{2})\d{4}$")


def detect_day_first(sample_values: list) -> bool:
    """Determines, ONCE for a whole column, whether its ambiguous D/M/Y
    or M/D/Y-style values (e.g. '03/04/2024', or compact '03042024')
    use a day-first or month-first convention - decided from evidence
    in the data itself, never guessed per value and never left to flip
    inconsistently row to row. A value with its first number > 12
    proves day-first (it can't be a month); a value with its second
    number > 12 proves month-first. If NOTHING in the sample settles it
    (every value has both numbers <= 12 - genuinely ambiguous), defaults
    to day-first (the ISO/international convention) - a documented,
    consistent choice rather than a per-value coin flip."""
    for value in sample_values:
        if value is None:
            continue
        text = str(value).strip()
        match = _AMBIGUOUS_DMY_PATTERN.match(text) or _AMBIGUOUS_COMPACT_PATTERN.match(text)
        if not match:
            continue
        first, second = int(match.group(1)), int(match.group(2))
        if first > 12:
            return True
        if second > 12:
            return False
    return True


def _parse_iso8601(value: str) -> date | datetime | None:
    """Parses an ISO 8601 string, or returns None if it is not one.

    ISO 8601 is written YEAR FIRST, so it is never ambiguous: `2021-04-07` is
    the 7th of April whatever the day-first convention of the column. The
    `dayfirst` flag exists for strings such as `03/04/2024` and must never be
    applied to an ISO value: dateutil swaps day and month whenever the day is
    12 or less when it is, which turned April 7th into July 4th for every FHIR
    date (a FHIR date carries a UTC offset, which none of the fast formats
    above accepts, so it used to fall through to dateutil with dayfirst=True).

    A value with an offset is converted to UTC and returned without a
    timezone. The Z of a CSV export is already UTC, so the same instant gives
    the same value whichever format wrote it, and no timezone-aware value
    reaches the columns of the tables, where two offsets in one column (winter
    and summer time) would not mix. A value with no time part (a year, or a
    year and a month, which FHIR allows) is a date."""
    try:
        parsed = dateutil.parser.isoparse(value)
    except (ValueError, OverflowError):
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed if ("T" in value or " " in value) else parsed.date()


def parse_date(value: str, dayfirst: bool = True) -> date | datetime | None:
    """Parses a date OR datetime string. Tries a fast, explicit list of
    UNAMBIGUOUS formats first (year always first - no day/month
    guessing involved); anything else falls through to
    `dateutil.parser.parse()`, which handles both the vast majority of
    real-world date formats AND the day-first/month-first ambiguity via
    `dayfirst` - this is what keeps the framework source-agnostic: a
    new export's date convention never needs a hardcoded pattern added
    here, and an ambiguous D/M/Y-style column is resolved from actual
    evidence in the data (see detect_day_first), not a blind guess.

    Returns a `datetime` when the value includes a time component, a
    plain `date` otherwise, or None if nothing could be parsed at all
    (rather than raising, so one bad value doesn't crash the whole
    column)."""
    value = (value or "").strip()
    if not value:
        return None
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    # Compact 8-digit date with no separator (e.g. "02132026") - %Y%m%d
    # above already handles the unambiguous year-first case; the
    # remaining MM/DD vs DD/MM order is ambiguous and resolved using the
    # SAME dayfirst convention detected for this column, never a fixed
    # try-order (which would silently favor one convention regardless
    # of what the source actually means). dateutil is deliberately not
    # trusted here - it's unreliable on bare digit strings with no
    # separators to anchor field boundaries.
    if len(value) == 8 and value.isdigit():
        order = ("%d%m%Y", "%m%d%Y") if dayfirst else ("%m%d%Y", "%d%m%Y")
        for fmt in order:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

    # ISO 8601 (for example a FHIR date with a UTC offset) is year first and
    # unambiguous: it never reaches the dayfirst-aware fallback below.
    iso = _parse_iso8601(value)
    if iso is not None:
        return iso

    try:
        parsed = dateutil.parser.parse(value, default=datetime(2000, 1, 1, 0, 0, 0), dayfirst=dayfirst)
    except (ValueError, OverflowError, TypeError):
        return None
    if parsed.time() == _MIDNIGHT:
        # No time component was present in the string (or it was a
        # genuine midnight timestamp - an acceptable, rare edge case to
        # treat as date-only, since assuming "midnight" for an
        # unspecified time is the standard convention).
        return parsed.date()
    return parsed


def cast_integer(value: str) -> int | None:
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def cast_decimal(value: str) -> float | None:
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


_TRUE_VALUES = {"1", "true", "t", "yes", "y", "oui"}
_FALSE_VALUES = {"0", "false", "f", "no", "n", "non"}


def normalize_boolean(value: str) -> bool | None:
    v = str(value).strip().lower()
    if v in _TRUE_VALUES:
        return True
    if v in _FALSE_VALUES:
        return False
    return None
