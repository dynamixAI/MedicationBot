"""
delete_flow.py

Delete medication confirmation flow.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from medbot.handlers.medication.list_screen import (
    build_medication_list_screen,
    medication_list_keyboard,
)
from medbot.medication_manager import get_medication, remove_medication
from medbot.storage import load_records, save_records


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


def delete_confirmation_keyboard(medication_id: str) -> InlineKeyboardMarkup:
    """Delete confirmation keyboard."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "❌ Yes, delete medication",
                    callback_data=f"med_delete_confirm_{medication_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Cancel",
                    callback_data=f"med_view_{medication_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 Home",
                    callback_data="menu_home",
                )
            ],
        ]
    )


def clear_schedules_for_medication(
    medication_id: str,
    owner_id: str,
) -> None:
    """Remove schedules for deleted medication."""
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


def clear_reminder_states_for_medication(
    medication_id: str,
    owner_id: str,
) -> None:
    """Remove reminder states for deleted medication."""
    reminder_states = load_records(REMINDER_STATE_FILE)

    kept_states = [
        state
        for state in reminder_states
        if not (
            state.get("owner_id") == owner_id
            and state.get("medication_id") == medication_id
        )
    ]

    save_records(REMINDER_STATE_FILE, kept_states, REMINDER_STATE_HEADERS)


async def start_delete_medication(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    medication_id: str,
) -> None:
    """Show delete confirmation screen."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        await query.edit_message_text("I couldn't find that medication.")
        return

    await query.edit_message_text(
        "❌ Delete Medication\n\n"
        f"{medication['name']} {medication['strength']}\n\n"
        "Are you sure you want to delete this medication?\n\n"
        "This will remove:\n"
        "• The medication\n"
        "• Its reminder times\n"
        "• Any pending reminders\n\n"
        "This cannot be undone.",
        reply_markup=delete_confirmation_keyboard(medication_id),
    )


async def confirm_delete_medication(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    medication_id: str,
) -> None:
    """Delete medication after confirmation."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        await query.edit_message_text("I couldn't find that medication.")
        return

    clear_schedules_for_medication(medication_id, owner_id)
    clear_reminder_states_for_medication(medication_id, owner_id)
    remove_medication(medication_id)

    await query.edit_message_text(
        "✅ Medication deleted.\n\n"
        f"{medication['name']} {medication['strength']} has been removed."
    )

    await query.message.reply_text(
        build_medication_list_screen(owner_id),
        reply_markup=medication_list_keyboard(owner_id),
    )