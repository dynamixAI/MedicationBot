"""
add_flow.py

Guided add-medication flow.
"""

import re
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from medbot.medication_manager import add_medication
from medbot.schedule_manager import add_schedule
from medbot.time_parser import parse_time_list, recommend_times
from medbot.handlers.medication.list_screen import (
    build_medication_list_screen,
    medication_list_keyboard,
)


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel keyboard."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data="med_cancel")]]
    )


def dose_unit_options() -> dict[str, str]:
    """Available medication form options."""
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
    """Build medication form question."""
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


def extract_number(text: str) -> Optional[str]:
    """Extract the first number from user text."""
    match = re.search(r"\d+", text)

    if not match:
        return None

    return match.group(0)


def dose_amount_question(dose_unit: str) -> str:
    """Build dose amount question based on medication form."""
    if dose_unit == "ml":
        return (
            "How many ml should be taken per dose?\n\n"
            "Examples:\n"
            "5\n"
            "10ml\n"
            "20 ml"
        )

    if dose_unit == "puff":
        return (
            "How many puffs should be taken per dose?\n\n"
            "Examples:\n"
            "1\n"
            "2 puffs"
        )

    if dose_unit == "application":
        return (
            "How many applications should be used per dose?\n\n"
            "Examples:\n"
            "1\n"
            "2"
        )

    return (
        f"How many {dose_unit}s should be taken per dose?\n\n"
        "Examples:\n"
        "1\n"
        "2"
    )


def stock_amount_question(dose_unit: str) -> str:
    """Build stock amount question based on medication form."""
    if dose_unit == "ml":
        return (
            "How many ml do you currently have?\n\n"
            "Examples:\n"
            "500\n"
            "500ml\n"
            "500 ml"
        )

    if dose_unit == "puff":
        return (
            "How many puffs do you currently have?\n\n"
            "Examples:\n"
            "120\n"
            "120 puffs"
        )

    if dose_unit == "application":
        return (
            "How many applications do you currently have?\n\n"
            "Examples:\n"
            "30\n"
            "30 applications"
        )

    return (
        f"How many {dose_unit}s do you currently have?\n\n"
        "Examples:\n"
        "28\n"
        "56\n"
        "100"
    )


async def start_add_medication(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start medication add flow."""
    query = update.callback_query
    await query.answer()

    context.user_data["add_medication"] = {
        "step": "name",
        "data": {},
    }

    await query.edit_message_text(
        "➕ Add Medication\n\nWhat is the medication name?",
        reply_markup=cancel_keyboard(),
    )


async def handle_add_medication_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle add medication text flow."""
    flow = context.user_data.get("add_medication")

    if not flow:
        return False

    owner_id = str(update.effective_user.id)
    text = update.message.text.strip()
    step = flow["step"]
    data = flow["data"]

    if step == "name":
        data["name"] = text.title()
        flow["step"] = "strength"

        await update.message.reply_text(
            "What strength is it?\n\nExample: 500mg"
        )
        return True

    if step == "strength":
        data["strength"] = text
        flow["step"] = "dose_unit"

        await update.message.reply_text(dose_unit_question())
        return True

    if step == "dose_unit":
        options = dose_unit_options()

        if text not in options:
            await update.message.reply_text(
                "Please choose a number from 1 to 8.\n\n"
                + dose_unit_question()
            )
            return True

        data["dose_unit"] = options[text]
        flow["step"] = "dose_amount"

        await update.message.reply_text(
            dose_amount_question(data["dose_unit"])
        )
        return True

    if step == "dose_amount":
        number = extract_number(text)

        if number is None:
            await update.message.reply_text(
                "Please enter a number.\n\n"
                + dose_amount_question(data["dose_unit"])
            )
            return True

        data["dose_amount"] = number
        flow["step"] = "stock_remaining"

        await update.message.reply_text(
            stock_amount_question(data["dose_unit"])
        )
        return True

    if step == "stock_remaining":
        number = extract_number(text)

        if number is None:
            await update.message.reply_text(
                "Please enter a number.\n\n"
                + stock_amount_question(data["dose_unit"])
            )
            return True

        data["stock_remaining"] = number
        flow["step"] = "times_per_day"

        await update.message.reply_text(
            "How many times per day should this medication be taken?\n\n"
            "Example: 1, 2, 3 or 4"
        )
        return True

    if step == "times_per_day":
        number = extract_number(text)

        if number is None:
            await update.message.reply_text("Please enter a number, for example: 3")
            return True

        times_per_day = int(number)

        if times_per_day < 1:
            await update.message.reply_text("Please enter at least 1 time per day.")
            return True

        data["times_per_day"] = str(times_per_day)

        suggested_times = recommend_times(times_per_day)

        if suggested_times:
            data["suggested_times"] = suggested_times
            flow["step"] = "confirm_times"

            await update.message.reply_text(
                "I recommend these reminder times:\n\n"
                f"{', '.join(suggested_times)}\n\n"
                "Reply yes to use these times, or enter your own times.\n\n"
                "Examples:\n"
                "9am, 1pm, 9pm\n"
                "08:00, 14:00, 20:00"
            )
            return True

        flow["step"] = "custom_times"

        await update.message.reply_text(
            "Please enter the reminder times separated by commas.\n\n"
            "Examples:\n"
            "9am, 1pm, 9pm\n"
            "08:00, 12:00, 16:00, 20:00"
        )
        return True

    if step == "confirm_times":
        if text.lower() in ["yes", "y", "ok", "okay"]:
            times = data["suggested_times"]
        else:
            parsed_times = parse_time_list(text)

            if parsed_times is None:
                await update.message.reply_text(
                    "I couldn't understand those times.\n\n"
                    "Please try again, for example:\n"
                    "9am, 1pm, 9pm"
                )
                return True

            times = parsed_times

        medication = add_medication(
            name=data["name"],
            strength=data["strength"],
            dose_amount=data["dose_amount"],
            dose_unit=data["dose_unit"],
            stock_remaining=data["stock_remaining"],
            owner_id=owner_id,
        )

        for reminder_time in times:
            add_schedule(
                medication_id=medication["medication_id"],
                time=reminder_time,
                owner_id=owner_id,
            )

        context.user_data.pop("add_medication", None)

        await update.message.reply_text("✅ Medication added successfully.")

        await update.message.reply_text(
            build_medication_list_screen(owner_id),
            reply_markup=medication_list_keyboard(owner_id),
        )

        return True

    if step == "custom_times":
        parsed_times = parse_time_list(text)

        if parsed_times is None:
            await update.message.reply_text(
                "I couldn't understand those times.\n\n"
                "Please try again, for example:\n"
                "9am, 1pm, 9pm"
            )
            return True

        medication = add_medication(
            name=data["name"],
            strength=data["strength"],
            dose_amount=data["dose_amount"],
            dose_unit=data["dose_unit"],
            stock_remaining=data["stock_remaining"],
            owner_id=owner_id,
        )

        for reminder_time in parsed_times:
            add_schedule(
                medication_id=medication["medication_id"],
                time=reminder_time,
                owner_id=owner_id,
            )

        context.user_data.pop("add_medication", None)

        await update.message.reply_text("✅ Medication added successfully.")

        await update.message.reply_text(
            build_medication_list_screen(owner_id),
            reply_markup=medication_list_keyboard(owner_id),
        )

        return True

    return False