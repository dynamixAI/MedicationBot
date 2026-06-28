"""
history_screen.py

Medication history and adherence screen.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from medbot.medication_manager import get_medication
from medbot.storage import load_records


REMINDER_STATE_FILE = "reminder_state.csv"


def history_keyboard(medication_id: str) -> InlineKeyboardMarkup:
    """Medication history navigation keyboard."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ Back to Medication",
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


def plural_unit(unit: str, quantity: int) -> str:
    """Return pluralised unit."""
    if quantity == 1:
        return unit

    if unit == "ml":
        return "ml"

    if unit.endswith("s"):
        return unit

    return f"{unit}s"


def get_medication_history(
    medication_id: str,
    owner_id: str,
) -> list[dict[str, str]]:
    """Return confirmed reminder history for a medication."""
    states = load_records(REMINDER_STATE_FILE)

    history = [
        state
        for state in states
        if state.get("owner_id") == owner_id
        and state.get("medication_id") == medication_id
        and state.get("confirmed") == "true"
    ]

    return sorted(
        history,
        key=lambda item: (
            item.get("scheduled_date", ""),
            item.get("scheduled_time", ""),
        ),
        reverse=True,
    )


def build_medication_history_screen(
    medication_id: str,
    owner_id: str,
) -> str:
    """Build medication history screen."""
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        return "I couldn't find that medication."

    history = get_medication_history(medication_id, owner_id)

    taken_count = len(
        [item for item in history if item.get("status") == "taken"]
    )
    skipped_count = len(
        [item for item in history if item.get("status") == "skipped"]
    )

    completed_count = taken_count + skipped_count

    if completed_count > 0:
        adherence = round((taken_count / completed_count) * 100)
        adherence_text = f"{adherence}%"
    else:
        adherence_text = "No data yet"

    dose_amount = int(medication.get("dose_amount", "0"))
    dose_unit = medication.get("dose_unit", "unit")
    stock = int(medication.get("stock_remaining", "0"))

    stock_unit = plural_unit(dose_unit, stock)
    dose_unit_text = plural_unit(dose_unit, dose_amount)

    screen = (
        "📋 Medication History\n\n"
        f"💊 {medication['name']} {medication['strength']}\n\n"
        "📊 Summary\n\n"
        f"✅ Doses taken\n{taken_count}\n\n"
        f"❌ Doses skipped\n{skipped_count}\n\n"
        f"📈 Adherence\n{adherence_text}\n\n"
        f"📦 Current stock\n{stock} {stock_unit}\n\n"
        "────────────────\n\n"
        "Recent Activity\n\n"
    )

    if not history:
        return (
            screen
            + "No medication activity recorded yet.\n\n"
            + "Once reminders are confirmed or skipped, they will appear here."
        )

    recent_items = history[:10]
    activity_lines = []

    for item in recent_items:
        status = item.get("status", "unknown")
        scheduled_date = item.get("scheduled_date", "")
        scheduled_time = item.get("scheduled_time", "")

        if status == "taken":
            icon = "✅"
            title = "Taken"
        elif status == "skipped":
            icon = "❌"
            title = "Skipped"
        else:
            icon = "•"
            title = status.title()

        activity_lines.append(
            f"{icon} {title}\n"
            f"{scheduled_date} • {scheduled_time}\n\n"
            "Dose\n"
            f"{dose_amount} {dose_unit_text}"
        )

    return screen + "\n\n────────────────\n\n".join(activity_lines)


async def show_medication_history_screen(
    update: Update,
    medication_id: str,
) -> None:
    """Show medication history screen."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)

    await query.edit_message_text(
        build_medication_history_screen(medication_id, owner_id),
        reply_markup=history_keyboard(medication_id),
    )