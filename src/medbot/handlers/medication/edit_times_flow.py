"""
edit_times_flow.py

Edit medication reminder times flow.
"""

from telegram import Update
from telegram.ext import ContextTypes

from medbot.handlers.medication.detail_screen import (
    build_medication_detail_screen,
    medication_detail_keyboard,
)
from medbot.medication_manager import get_medication
from medbot.schedule_manager import add_schedule, get_schedules_for_medication
from medbot.storage import load_records, save_records
from medbot.time_parser import parse_time_list


SCHEDULE_FILE = "medication_schedule.csv"
REMINDER_STATE_FILE = "reminder_state.csv"

SCHEDULE_HEADERS = [
    "owner_id",
    "schedule_id",
    "medication_id",
    "time",
    "active",
]

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


def replace_schedules_for_medication(
    medication_id: str,
    owner_id: str,
    times: list[str],
) -> None:
    """Replace reminder schedules for one medication."""
    schedules = load_records(SCHEDULE_FILE)

    kept_schedules = [
        schedule
        for schedule in schedules
        if not (
            schedule.get("owner_id") == owner_id
            and schedule.get("medication_id") == medication_id
        )
    ]

    save_records(SCHEDULE_FILE, kept_schedules, SCHEDULE_HEADERS)

    for reminder_time in times:
        add_schedule(
            medication_id=medication_id,
            time=reminder_time,
            owner_id=owner_id,
        )


def clear_pending_reminder_states(
    medication_id: str,
    owner_id: str,
) -> None:
    """Clear unconfirmed reminder states after reminder times change."""
    reminder_states = load_records(REMINDER_STATE_FILE)

    kept_states = [
        state
        for state in reminder_states
        if not (
            state.get("owner_id") == owner_id
            and state.get("medication_id") == medication_id
            and state.get("confirmed") != "true"
        )
    ]

    save_records(REMINDER_STATE_FILE, kept_states, REMINDER_STATE_HEADERS)


async def start_edit_times(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    medication_id: str,
) -> None:
    """Start edit reminder times flow."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        await query.edit_message_text("I couldn't find that medication.")
        return

    schedules = get_schedules_for_medication(medication_id, owner_id)
    current_times = sorted(schedule["time"] for schedule in schedules)

    if current_times:
        current_time_text = "\n".join(f"• {time}" for time in current_times)
    else:
        current_time_text = "No reminder times set."

    context.user_data["edit_medication_times"] = {
        "medication_id": medication_id,
    }

    await query.edit_message_text(
        "🕒 Edit Reminder Times\n\n"
        f"{medication['name']} {medication['strength']}\n\n"
        "Current reminders:\n"
        f"{current_time_text}\n\n"
        "Type the new reminder times separated by commas.\n\n"
        "Examples:\n"
        "09:00, 15:00, 21:00\n"
        "9am, 3pm, 9pm"
    )


async def handle_edit_times_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle new reminder times."""
    flow = context.user_data.get("edit_medication_times")

    if not flow:
        return False

    owner_id = str(update.effective_user.id)
    medication_id = flow["medication_id"]
    text = update.message.text.strip()

    parsed_times = parse_time_list(text)

    if parsed_times is None:
        await update.message.reply_text(
            "I couldn't understand those times.\n\n"
            "Please try again, for example:\n"
            "09:00, 15:00, 21:00\n"
            "9am, 3pm, 9pm"
        )
        return True

    replace_schedules_for_medication(
        medication_id=medication_id,
        owner_id=owner_id,
        times=parsed_times,
    )

    clear_pending_reminder_states(
        medication_id=medication_id,
        owner_id=owner_id,
    )

    context.user_data.pop("edit_medication_times", None)

    await update.message.reply_text("✅ Reminder times updated.")

    await update.message.reply_text(
        build_medication_detail_screen(medication_id, owner_id),
        reply_markup=medication_detail_keyboard(medication_id),
    )

    return True