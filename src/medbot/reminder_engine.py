"""
reminder_engine.py

Finds medication reminders and caregiver alerts due now.
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
    return datetime.fromisoformat(f"{scheduled_date}T{scheduled_time}")


def get_due_reminders(now: datetime | None = None) -> list[dict[str, str]]:
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

        if state.get("confirmed") == "true":
            continue

        now_time = now.strftime("%H:%M")
        snoozed_until = state.get("snoozed_until", "")
        minutes_difference = int((now - scheduled_at).total_seconds() // 60)

        reminder_types = []

        if snoozed_until:
            if now_time == snoozed_until:
                reminder_types.append("repeat")
                update_reminder_state(state["dose_id"], {"snoozed_until": ""})
        else:
            if minutes_difference == -15 and state.get("pre_reminder_sent") != "true":
                reminder_types.append("pre")
                mark_reminder_sent(state["dose_id"], "pre")

            if minutes_difference == 0 and state.get("due_reminder_sent") != "true":
                reminder_types.append("due")
                mark_reminder_sent(state["dose_id"], "due")

            if minutes_difference > 0 and minutes_difference % 5 == 0:
                reminder_types.append("repeat")

            if minutes_difference >= 30 and state.get("caregiver_thirty_sent") != "true":
                reminder_types.append("caregiver_thirty")
                mark_reminder_sent(state["dose_id"], "caregiver_thirty")

            if minutes_difference >= 60 and state.get("caregiver_sixty_sent") != "true":
                reminder_types.append("caregiver_sixty")
                mark_reminder_sent(state["dose_id"], "caregiver_sixty")

        for reminder_type in reminder_types:
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