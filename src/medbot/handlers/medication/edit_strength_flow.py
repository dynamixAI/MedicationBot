"""
edit_strength_flow.py

Edit medication strength flow.
"""

from telegram import Update
from telegram.ext import ContextTypes

from medbot.medication_manager import edit_medication, get_medication
from medbot.handlers.medication.detail_screen import (
    build_medication_detail_screen,
    medication_detail_keyboard,
)


async def start_edit_strength(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    medication_id: str,
) -> None:
    """Start edit medication strength flow."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        await query.edit_message_text("I couldn't find that medication.")
        return

    context.user_data["edit_medication_strength"] = {
        "medication_id": medication_id,
    }

    await query.edit_message_text(
        "💪 Edit Medication Strength\n\n"
        f"Current strength:\n{medication['strength']}\n\n"
        "Please type the new strength.\n\n"
        "Examples:\n"
        "500mg\n"
        "20mg\n"
        "250mg/5ml"
    )


async def handle_edit_strength_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle new medication strength."""
    flow = context.user_data.get("edit_medication_strength")

    if not flow:
        return False

    owner_id = str(update.effective_user.id)
    medication_id = flow["medication_id"]
    new_strength = update.message.text.strip()

    edit_medication(
        medication_id,
        {"strength": new_strength},
    )

    context.user_data.pop("edit_medication_strength", None)

    await update.message.reply_text("✅ Medication strength updated.")

    await update.message.reply_text(
        build_medication_detail_screen(medication_id, owner_id),
        reply_markup=medication_detail_keyboard(medication_id),
    )

    return True