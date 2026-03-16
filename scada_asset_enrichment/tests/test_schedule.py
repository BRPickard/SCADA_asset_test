from datetime import date

from src.schedule.planner import calculate_next_due


def test_next_due_prefers_last_service_date():
    due = calculate_next_due("2024-01-01", "2023-01-01", 180)
    assert due == date(2024, 6, 29)


def test_next_due_falls_back_to_install_date():
    due = calculate_next_due(None, "2024-03-15", 90)
    assert due == date(2024, 6, 13)


def test_next_due_missing_dates():
    assert calculate_next_due(None, None, 90) is None
