"""
schedule_manager.py

Business logic for medication reminder schedules.
"""

from typing import Dict, List

from medbot.storage import (
    append_record,
    delete_record,
    get_next_id,
    load_records,
)


SCHEDULE_FILE = "medication_schedule.csv"

SCHEDULE_HEADERS = [
    "schedule_id",
    "medication_id",
    "time",
    "active",
]


def list_schedules() -> List[Dict[str, str]]:
    """Return all medication schedules."""
    return load_records(SCHEDULE_FILE)


def get_schedules_for_medication(medication_id: str) -> List[Dict[str, str]]:
    """Return all active schedules for a medication."""
    schedules = load_records(SCHEDULE_FILE)

    return [
        schedule
        for schedule in schedules
        if schedule.get("medication_id") == medication_id
        and schedule.get("active") == "true"
    ]


def add_schedule(medication_id: str, time: str) -> Dict[str, str]:
    """Add a reminder time for a medication."""
    schedule = {
        "schedule_id": get_next_id(SCHEDULE_FILE, "schedule_id"),
        "medication_id": medication_id,
        "time": time,
        "active": "true",
    }

    append_record(SCHEDULE_FILE, schedule, SCHEDULE_HEADERS)
    return schedule


def remove_schedule(schedule_id: str) -> bool:
    """Remove a reminder schedule."""
    return delete_record(
        SCHEDULE_FILE,
        "schedule_id",
        schedule_id,
        SCHEDULE_HEADERS,
    )


def remove_schedules_for_medication(medication_id: str) -> int:
    """Remove all schedules for a medication. Returns number removed."""
    schedules = load_records(SCHEDULE_FILE)
    matching = [
        schedule
        for schedule in schedules
        if schedule.get("medication_id") == medication_id
    ]

    count = 0

    for schedule in matching:
        removed = remove_schedule(schedule["schedule_id"])
        if removed:
            count += 1

    return count