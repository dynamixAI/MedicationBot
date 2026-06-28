"""
activity_manager.py

Unified activity logging for MediBot.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from medbot.storage import append_record, get_next_id, load_records


ACTIVITY_FILE = "activity_history.csv"

ACTIVITY_HEADERS = [
    "owner_id",
    "event_id",
    "event_type",
    "medication_id",
    "title",
    "details",
    "old_value",
    "new_value",
    "event_date",
    "event_time",
]


def current_uk_datetime() -> datetime:
    """Return current UK local datetime."""
    return datetime.now(ZoneInfo("Europe/London"))


def log_activity(
    owner_id: str,
    event_type: str,
    title: str,
    medication_id: str = "",
    details: str = "",
    old_value: str = "",
    new_value: str = "",
) -> dict[str, str]:
    """Log a user activity event."""
    now = current_uk_datetime()

    activity = {
        "owner_id": owner_id,
        "event_id": get_next_id(ACTIVITY_FILE, "event_id"),
        "event_type": event_type,
        "medication_id": medication_id,
        "title": title,
        "details": details,
        "old_value": old_value,
        "new_value": new_value,
        "event_date": now.date().isoformat(),
        "event_time": now.strftime("%H:%M"),
    }

    append_record(ACTIVITY_FILE, activity, ACTIVITY_HEADERS)
    return activity


def list_activities(owner_id: str) -> list[dict[str, str]]:
    """Return all activities for an owner, newest first."""
    activities = load_records(ACTIVITY_FILE)

    owner_activities = [
        activity
        for activity in activities
        if activity.get("owner_id") == owner_id
    ]

    return sorted(
        owner_activities,
        key=lambda item: (
            item.get("event_date", ""),
            item.get("event_time", ""),
            item.get("event_id", ""),
        ),
        reverse=True,
    )


def list_medication_activities(
    owner_id: str,
    medication_id: str,
) -> list[dict[str, str]]:
    """Return activities for one medication, newest first."""
    activities = list_activities(owner_id)

    return [
        activity
        for activity in activities
        if activity.get("medication_id") == medication_id
    ]