from datetime import date

from src.common.time_utils import duration_minutes, week_bounds


def test_duration_minutes():
    assert duration_minutes("09:00", "10:30") == 90


def test_week_bounds_is_monday_to_sunday():
    assert week_bounds(date(2026, 11, 21)) == (date(2026, 11, 16), date(2026, 11, 22))
