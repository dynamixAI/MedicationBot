"""
edit_menu.py

Medication edit menu screen.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from medbot.medication_manager import get_medication


def edit_medication_keyboard(medication_id: str) -> InlineKeyboardMarkup:
    """Edit medication menu keyboard."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📝 Name", callback_data=f"med_edit_name_{medication_id}")],
            [InlineKeyboardButton("💪 Strength", callback_data=f"med_edit_strength_{medication_id}")],
            [InlineKeyboardButton("💊 Dose", callback_data=f"med_edit_dose_{medication_id}")],
            [InlineKeyboardButton("🕒 Reminder Times", callback_data=f"med_edit_times_{medication_id}")],
            [InlineKeyboardButton("📦 Stock", callback_data=f"med_edit_stock_{medication_id}")],
            [InlineKeyboardButton("⬅️ Back to Medication", callback_data=f"med_view_{medication_id}")],
            [InlineKeyboardButton("🏠 Home", callback_data="menu_home")],
        ]
    )


def build_edit_medication_screen(medication_id: str, owner_id: str) -> str:
    """Build edit medication menu screen."""
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        return "I couldn't find that medication."

    return (
        "✏️ Edit Medication\n\n"
        f"{medication['name']} {medication['strength']}\n\n"
        "What would you like to change?"
    )


async def show_edit_medication_menu(update: Update, medication_id: str) -> None:
    """Show edit medication menu."""
    query = update.callback_query

    owner_id = str(query.from_user.id)

    await query.edit_message_text(
        build_edit_medication_screen(medication_id, owner_id),
        reply_markup=edit_medication_keyboard(medication_id),
    )