"""
refill_flow.py

Guided refill-medication flow.
"""

from telegram import Update
from telegram.ext import ContextTypes

from medbot.inventory_manager import add_refill
from medbot.medication_manager import get_medication
from medbot.handlers.medication.add_flow import extract_number
from medbot.handlers.medication.detail_screen import (
    build_medication_detail_screen,
    medication_detail_keyboard,
)


def plural_unit(unit: str, quantity: int) -> str:
    """Return a simple pluralised unit."""
    if quantity == 1:
        return unit

    if unit == "ml":
        return "ml"

    if unit.endswith("s"):
        return unit

    return f"{unit}s"


async def select_refill_medication(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    medication_id: str,
) -> None:
    """Start refill from selected medication detail."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        await query.edit_message_text("I couldn't find that medication.")
        return

    dose_unit = medication.get("dose_unit", "unit")
    stock = int(medication.get("stock_remaining", "0"))

    context.user_data["refill_medication"] = {
        "medication_id": medication["medication_id"],
        "name": medication["name"],
        "strength": medication["strength"],
        "dose_unit": dose_unit,
    }

    await query.edit_message_text(
        "📦 Refill Stock\n\n"
        f"{medication['name']} {medication['strength']}\n\n"
        "Current stock\n"
        f"{stock} {plural_unit(dose_unit, stock)}\n\n"
        f"How many {plural_unit(dose_unit, 2)} did you receive?"
    )


async def handle_refill_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle refill quantity input."""
    refill = context.user_data.get("refill_medication")

    if not refill:
        return False

    owner_id = str(update.effective_user.id)
    text = update.message.text.strip()
    quantity_added = extract_number(text)

    if quantity_added is None:
        await update.message.reply_text(
            "Please enter a number, for example: 56"
        )
        return True

    success = add_refill(
        medication_id=refill["medication_id"],
        quantity_added=quantity_added,
        owner_id=owner_id,
    )

    if not success:
        await update.message.reply_text(
            "I couldn't update that medication. Please try again."
        )
        return True

    context.user_data.pop("refill_medication", None)

    medication = get_medication(refill["medication_id"], owner_id)
    dose_unit = refill.get("dose_unit", "unit")
    added = int(quantity_added)

    if medication is None:
        await update.message.reply_text("✅ Refill added successfully.")
        return True

    current_stock = int(medication.get("stock_remaining", "0"))

    await update.message.reply_text(
        "✅ Stock Updated\n\n"
        f"{medication['name']} {medication['strength']}\n\n"
        "You added\n"
        f"{added} {plural_unit(dose_unit, added)}\n\n"
        "Current stock\n"
        f"{current_stock} {plural_unit(dose_unit, current_stock)}"
    )

    await update.message.reply_text(
        build_medication_detail_screen(refill["medication_id"], owner_id),
        reply_markup=medication_detail_keyboard(refill["medication_id"]),
    )

    return True