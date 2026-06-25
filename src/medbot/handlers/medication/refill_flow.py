"""
refill_flow.py

Guided refill-medication flow.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from medbot.inventory_manager import add_refill
from medbot.medication_manager import list_medications
from medbot.handlers.medication.add_flow import cancel_keyboard
from medbot.handlers.medication.list_screen import (
    build_medication_list_screen,
    medication_list_keyboard,
)


async def start_refill_medication(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show medication selection before refill."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medications = list_medications(owner_id)

    if not medications:
        await query.edit_message_text(
            "📦 Refill Medication\n\n"
            "You have not added any medications yet.",
            reply_markup=medication_list_keyboard(owner_id),
        )
        return

    buttons = []

    for medication in medications:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{medication['name']} {medication['strength']}",
                    callback_data=f"med_refill_select_{medication['medication_id']}",
                )
            ]
        )

    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_medications")])

    await query.edit_message_text(
        "📦 Refill Medication\n\n"
        "Which medication did you receive?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def select_refill_medication(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    medication_id: str,
) -> None:
    """Select a medication for refill."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medications = list_medications(owner_id)

    medication = next(
        (
            item
            for item in medications
            if item["medication_id"] == medication_id
        ),
        None,
    )

    if medication is None:
        await query.edit_message_text(
            "I couldn't find that medication.",
            reply_markup=medication_list_keyboard(owner_id),
        )
        return

    context.user_data["refill_medication"] = {
        "medication_id": medication["medication_id"],
        "name": medication["name"],
        "strength": medication["strength"],
    }

    await query.edit_message_text(
        "📦 Refill Medication\n\n"
        f"Medication: {medication['name']} {medication['strength']}\n\n"
        "How many tablets/capsules did you receive?",
        reply_markup=cancel_keyboard(),
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

    if not text.isdigit():
        await update.message.reply_text(
            "Please enter a number, for example: 100"
        )
        return True

    quantity_added = text

    add_refill(
        medication_id=refill["medication_id"],
        quantity_added=quantity_added,
    )

    context.user_data.pop("refill_medication", None)

    await update.message.reply_text(
        "✅ Refill added successfully.\n\n"
        f"{refill['name']} {refill['strength']}\n"
        f"Added: {quantity_added}"
    )

    await update.message.reply_text(
        build_medication_list_screen(owner_id),
        reply_markup=medication_list_keyboard(owner_id),
    )

    return True