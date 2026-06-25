"""
list_screen.py

Medication list screen.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from medbot.medication_manager import list_medications


def medication_list_keyboard(owner_id: str) -> InlineKeyboardMarkup:
    """Medication list screen keyboard."""
    medications = list_medications(owner_id)

    buttons = []

    for medication in medications:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"🟢 {medication['name']} {medication['strength']}",
                    callback_data=f"med_view_{medication['medication_id']}",
                )
            ]
        )

    buttons.append([InlineKeyboardButton("➕ Add Medication", callback_data="med_add")])
    buttons.append([InlineKeyboardButton("⬅️ Home", callback_data="menu_home")])

    return InlineKeyboardMarkup(buttons)


def build_medication_list_screen(owner_id: str) -> str:
    """Build medication list screen."""
    medications = list_medications(owner_id)

    if not medications:
        return (
            "💊 My Medications\n\n"
            "You have not added any medications yet.\n\n"
            "Tap ➕ Add Medication to get started."
        )

    return (
        "💊 My Medications\n\n"
        f"You have {len(medications)} active medication(s).\n\n"
        "Choose one to view or manage."
    )


async def show_medications_screen(update: Update) -> None:
    """Show medication list screen."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)

    await query.edit_message_text(
        build_medication_list_screen(owner_id),
        reply_markup=medication_list_keyboard(owner_id),
    )