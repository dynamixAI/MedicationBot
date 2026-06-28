"""
edit_dose_flow.py

Edit medication dose flow.
"""

import re
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from medbot.medication_manager import edit_medication, get_medication
from medbot.handlers.medication.detail_screen import (
    build_medication_detail_screen,
    medication_detail_keyboard,
)


def extract_number(text: str) -> Optional[str]:
    """Extract first number from text."""
    match = re.search(r"\d+", text)

    if not match:
        return None

    return match.group(0)


def dose_unit_options() -> dict[str, str]:
    """Available dose unit options."""
    return {
        "1": "tablet",
        "2": "capsule",
        "3": "ml",
        "4": "puff",
        "5": "injection",
        "6": "application",
        "7": "patch",
        "8": "unit",
    }


def dose_unit_question() -> str:
    """Build dose unit question."""
    return (
        "What form is this medication?\n\n"
        "1. Tablet\n"
        "2. Capsule\n"
        "3. Liquid\n"
        "4. Puff / Inhaler\n"
        "5. Injection\n"
        "6. Cream / Ointment\n"
        "7. Patch\n"
        "8. Other\n\n"
        "Reply with the number."
    )


async def start_edit_dose(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    medication_id: str,
) -> None:
    """Start edit medication dose flow."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        await query.edit_message_text("I couldn't find that medication.")
        return

    context.user_data["edit_medication_dose"] = {
        "medication_id": medication_id,
        "step": "amount",
    }

    await query.edit_message_text(
        "💊 Edit Dose\n\n"
        f"Current dose:\n"
        f"{medication['dose_amount']} {medication.get('dose_unit', 'unit')}\n\n"
        "How much should be taken per dose?\n\n"
        "Examples:\n"
        "1\n"
        "2\n"
        "10"
    )


async def handle_edit_dose_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle edit dose text input."""
    flow = context.user_data.get("edit_medication_dose")

    if not flow:
        return False

    owner_id = str(update.effective_user.id)
    text = update.message.text.strip()
    medication_id = flow["medication_id"]
    step = flow["step"]

    if step == "amount":
        dose_amount = extract_number(text)

        if dose_amount is None:
            await update.message.reply_text(
                "Please enter a number.\n\n"
                "Examples:\n"
                "1\n"
                "2\n"
                "10"
            )
            return True

        flow["dose_amount"] = dose_amount
        flow["step"] = "unit"

        await update.message.reply_text(dose_unit_question())
        return True

    if step == "unit":
        options = dose_unit_options()

        if text not in options:
            await update.message.reply_text(
                "Please choose a number from 1 to 8.\n\n"
                + dose_unit_question()
            )
            return True

        dose_unit = options[text]

        edit_medication(
            medication_id,
            {
                "dose_amount": flow["dose_amount"],
                "dose_unit": dose_unit,
            },
        )

        context.user_data.pop("edit_medication_dose", None)

        await update.message.reply_text("✅ Medication dose updated.")

        await update.message.reply_text(
            build_medication_detail_screen(medication_id, owner_id),
            reply_markup=medication_detail_keyboard(medication_id),
        )

        return True

    return False