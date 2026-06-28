"""
reminder_engine.py

Finds medication reminders due now.
"""

from datetime import datetime

from medbot.medication_manager import get_medication
from medbot.reminder_state_manager import (
    get_or_create_reminder_state,
    mark_reminder_sent,
    update_reminder_state,
)
from medbot.storage import load_records


SCHEDULE_FILE = "medication_schedule.csv"


def parse_schedule_datetime(scheduled_date: str, scheduled_time: str) -> datetime:
    """Build datetime from date and HH:MM time."""
    return datetime.fromisoformat(f"{scheduled_date}T{scheduled_time}")


def get_reminder_type(
    now: datetime,
    scheduled_at: datetime,
    state: dict[str, str],
) -> str | None:
    """Return reminder type due at this moment."""
    if state.get("confirmed") == "true":
        return None

    now_time = now.strftime("%H:%M")
    snoozed_until = state.get("snoozed_until", "")

    if snoozed_until:
        if now_time == snoozed_until:
            return "repeat"
        return None

    minutes_difference = int((now - scheduled_at).total_seconds() // 60)

    if minutes_difference == -15 and state.get("pre_reminder_sent") != "true":
        return "pre"

    if minutes_difference == 0 and state.get("due_reminder_sent") != "true":
        return "due"

    if minutes_difference > 0 and minutes_difference % 5 == 0:
        return "repeat"

    return None


def get_due_reminders(now: datetime | None = None) -> list[dict[str, str]]:
    """Return reminders due now."""
    if now is None:
        now = datetime.now().replace(second=0, microsecond=0)

    scheduled_date = now.date().isoformat()
    schedules = load_records(SCHEDULE_FILE)
    due_reminders = []

    for schedule in schedules:
        if schedule.get("active") != "true":
            continue

        owner_id = schedule["owner_id"]
        medication_id = schedule["medication_id"]
        scheduled_time = schedule["time"]

        medication = get_medication(medication_id, owner_id)

        if medication is None:
            continue

        scheduled_at = parse_schedule_datetime(scheduled_date, scheduled_time)

        state = get_or_create_reminder_state(
            owner_id=owner_id,
            medication_id=medication_id,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
        )

        reminder_type = get_reminder_type(now, scheduled_at, state)

        if reminder_type is None:
            continue

        if reminder_type in ["pre", "due"]:
            mark_reminder_sent(state["dose_id"], reminder_type)

        if reminder_type == "repeat" and state.get("snoozed_until"):
            update_reminder_state(state["dose_id"], {"snoozed_until": ""})

        due_reminders.append(
            {
                "owner_id": owner_id,
                "dose_id": state["dose_id"],
                "medication_id": medication_id,
                "medication_name": medication["name"],
                "strength": medication["strength"],
                "dose_amount": medication["dose_amount"],
                "dose_unit": medication.get("dose_unit", "unit"),
                "scheduled_time": scheduled_time,
                "reminder_type": reminder_type,
            }
        )

    return due_reminders