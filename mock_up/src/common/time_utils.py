"""Pure helpers for time math — no I/O, easy to unit test."""
from __future__ import annotations

from datetime import date, timedelta


def to_minutes(hhmm: str) -> int:
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def duration_minutes(start: str, end: str) -> int:
    return to_minutes(end) - to_minutes(start)


def week_bounds(day: date) -> tuple[date, date]:
    """Monday..Sunday of the week containing `day`."""
    monday = day - timedelta(days=day.weekday())
    return monday, monday + timedelta(days=6)
