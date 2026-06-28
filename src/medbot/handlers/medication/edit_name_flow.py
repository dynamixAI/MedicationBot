"""
edit_name_flow.py

Edit medication name flow.
"""

from telegram import Update
from telegram.ext import ContextTypes

from medbot.medication_manager import edit_medication, get_medication
from medbot.handlers.medication.detail_screen import (
    build_medication_detail_screen,
    medication_detail_keyboard,
)


async def start_edit_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    medication_id: str,
) -> None:
    """Start edit medication name flow."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        await query.edit_message_text("I couldn't find that medication.")
        return

    context.user_data["edit_medication_name"] = {
        "medication_id": medication_id,
    }

    await query.edit_message_text(
        "📝 Edit Medication Name\n\n"
        f"Current name:\n{medication['name']}\n\n"
        "Please type the new medication name."
    )


async def handle_edit_name_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle new medication name."""
    flow = context.user_data.get("edit_medication_name")

    if not flow:
        return False

    owner_id = str(update.effective_user.id)
    medication_id = flow["medication_id"]
    new_name = update.message.text.strip().title()

    edit_medication(
        medication_id,
        {"name": new_name},
    )

    context.user_data.pop("edit_medication_name", None)

    await update.message.reply_text("✅ Medication name updated.")

    await update.message.reply_text(
        build_medication_detail_screen(medication_id, owner_id),
        reply_markup=medication_detail_keyboard(medication_id),
    )

    return True