"""
reminder_state_manager.py

Tracks reminder state for each scheduled medication dose.
"""

from datetime import date
from typing import Optional

from medbot.storage import append_record, find_record, load_records, update_record


REMINDER_STATE_FILE = "reminder_state.csv"

REMINDER_STATE_HEADERS = [
    "owner_id",
    "dose_id",
    "medication_id",
    "scheduled_date",
    "scheduled_time",
    "pre_reminder_sent",
    "due_reminder_sent",
    "thirty_min_sent",
    "sixty_min_sent",
    "caregiver_thirty_sent",
    "caregiver_sixty_sent",
    "snoozed_until",
    "confirmed",
    "status",
]


def build_dose_id(owner_id: str, medication_id: str, scheduled_date: str, scheduled_time: str) -> str:
    """Build unique dose ID."""
    return f"{owner_id}_{medication_id}_{scheduled_date}_{scheduled_time}"


def get_reminder_state(dose_id: str) -> Optional[dict[str, str]]:
    """Return reminder state by dose ID."""
    return find_record(REMINDER_STATE_FILE, "dose_id", dose_id)


def get_or_create_reminder_state(
    owner_id: str,
    medication_id: str,
    scheduled_time: str,
    scheduled_date: str | None = None,
) -> dict[str, str]:
    """Get or create reminder state for a scheduled dose."""
    if scheduled_date is None:
        scheduled_date = date.today().isoformat()

    dose_id = build_dose_id(owner_id, medication_id, scheduled_date, scheduled_time)
    existing_state = get_reminder_state(dose_id)

    if existing_state:
        return existing_state

    state = {
        "owner_id": owner_id,
        "dose_id": dose_id,
        "medication_id": medication_id,
        "scheduled_date": scheduled_date,
        "scheduled_time": scheduled_time,
        "pre_reminder_sent": "false",
        "due_reminder_sent": "false",
        "thirty_min_sent": "false",
        "sixty_min_sent": "false",
        "caregiver_thirty_sent": "false",
        "caregiver_sixty_sent": "false",
        "snoozed_until": "",
        "confirmed": "false",
        "status": "pending",
    }

    append_record(REMINDER_STATE_FILE, state, REMINDER_STATE_HEADERS)
    return state


def update_reminder_state(dose_id: str, updates: dict[str, str]) -> bool:
    """Update reminder state."""
    return update_record(
        REMINDER_STATE_FILE,
        "dose_id",
        dose_id,
        updates,
        REMINDER_STATE_HEADERS,
    )


def mark_reminder_sent(dose_id: str, reminder_type: str) -> bool:
    """Mark a reminder stage as sent."""
    field_map = {
        "pre": "pre_reminder_sent",
        "due": "due_reminder_sent",
        "thirty": "thirty_min_sent",
        "sixty": "sixty_min_sent",
        "caregiver_thirty": "caregiver_thirty_sent",
        "caregiver_sixty": "caregiver_sixty_sent",
    }

    field = field_map.get(reminder_type)

    if field is None:
        return False

    return update_reminder_state(dose_id, {field: "true"})


def mark_dose_snoozed(dose_id: str, snoozed_until: str) -> bool:
    """Mark dose as snoozed until a specific HH:MM time."""
    return update_reminder_state(
        dose_id,
        {
            "snoozed_until": snoozed_until,
            "status": "snoozed",
        },
    )


def mark_dose_confirmed(dose_id: str, status: str = "taken") -> bool:
    """Mark dose as confirmed."""
    return update_reminder_state(
        dose_id,
        {
            "confirmed": "true",
            "status": status,
            "snoozed_until": "",
        },
    )


def is_dose_confirmed(dose_id: str) -> bool:
    """Return whether dose has been confirmed."""
    state = get_reminder_state(dose_id)

    if not state:
        return False

    return state.get("confirmed") == "true"


def list_pending_reminder_states(owner_id: str) -> list[dict[str, str]]:
    """Return unconfirmed reminder states for an owner."""
    states = load_records(REMINDER_STATE_FILE)

    return [
        state
        for state in states
        if state.get("owner_id") == owner_id
        and state.get("confirmed") != "true"
    ]