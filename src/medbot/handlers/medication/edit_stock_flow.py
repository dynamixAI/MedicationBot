"""
edit_stock_flow.py

Edit medication stock flow.
"""

from telegram import Update
from telegram.ext import ContextTypes

from medbot.handlers.medication.add_flow import extract_number
from medbot.handlers.medication.detail_screen import (
    build_medication_detail_screen,
    medication_detail_keyboard,
)
from medbot.inventory_manager import set_stock
from medbot.medication_manager import get_medication


async def start_edit_stock(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    medication_id: str,
) -> None:
    """Start edit medication stock flow."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        await query.edit_message_text("I couldn't find that medication.")
        return

    dose_unit = medication.get("dose_unit", "unit")
    current_stock = medication.get("stock_remaining", "0")

    context.user_data["edit_medication_stock"] = {
        "medication_id": medication_id,
    }

    await query.edit_message_text(
        "📦 Edit Stock\n\n"
        f"{medication['name']} {medication['strength']}\n\n"
        "Current stock:\n"
        f"{current_stock} {dose_unit}\n\n"
        "Enter the correct stock amount.\n\n"
        "Examples:\n"
        "120\n"
        "120 tablets\n"
        "500ml"
    )


async def handle_edit_stock_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle corrected stock input."""
    flow = context.user_data.get("edit_medication_stock")

    if not flow:
        return False

    owner_id = str(update.effective_user.id)
    medication_id = flow["medication_id"]
    text = update.message.text.strip()

    corrected_stock = extract_number(text)

    if corrected_stock is None:
        await update.message.reply_text(
            "Please enter a number.\n\n"
            "Examples:\n"
            "120\n"
            "120 tablets\n"
            "500ml"
        )
        return True

    set_stock(
        medication_id=medication_id,
        new_stock=corrected_stock,
        owner_id=owner_id,
    )

    context.user_data.pop("edit_medication_stock", None)

    await update.message.reply_text("✅ Stock corrected.")

    await update.message.reply_text(
        build_medication_detail_screen(medication_id, owner_id),
        reply_markup=medication_detail_keyboard(medication_id),
    )

    return True