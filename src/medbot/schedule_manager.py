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
    "owner_id",
    "schedule_id",
    "medication_id",
    "time",
    "active",
]


def list_schedules(owner_id: str = "default") -> List[Dict[str, str]]:
    """Return all medication schedules for an owner."""
    schedules = load_records(SCHEDULE_FILE)

    return [
        schedule
        for schedule in schedules
        if schedule.get("owner_id") == owner_id
    ]


def get_schedules_for_medication(
    medication_id: str,
    owner_id: str = "default",
) -> List[Dict[str, str]]:
    """Return all active schedules for a medication."""
    return [
        schedule
        for schedule in list_schedules(owner_id)
        if schedule.get("medication_id") == medication_id
        and schedule.get("active") == "true"
    ]


def add_schedule(
    medication_id: str,
    time: str,
    owner_id: str = "default",
) -> Dict[str, str]:
    """Add a reminder time for a medication."""
    schedule = {
        "owner_id": owner_id,
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