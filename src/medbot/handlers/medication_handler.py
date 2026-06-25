"""
medication_handler.py

Telegram screens for medication management.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from medbot.medication_manager import add_medication, list_medications
from medbot.schedule_manager import add_schedule, get_schedules_for_medication


def medication_keyboard() -> InlineKeyboardMarkup:
    """Medication screen keyboard."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ Add Medication", callback_data="med_add")],
            [InlineKeyboardButton("⬅️ Home", callback_data="menu_home")],
        ]
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel keyboard."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("❌ Cancel", callback_data="med_cancel")]
        ]
    )


def build_medication_screen(owner_id: str) -> str:
    """Build medication dashboard text."""
    medications = list_medications(owner_id)

    if not medications:
        return (
            "💊 My Medications\n\n"
            "You have not added any medications yet.\n\n"
            "Tap ➕ Add Medication to get started."
        )

    lines = [
        "💊 My Medications",
        "",
        f"You currently have {len(medications)} active medication(s).",
        "",
    ]

    for medication in medications:
        schedules = get_schedules_for_medication(
            medication["medication_id"],
            owner_id,
        )

        dose_amount = int(medication.get("dose_amount", "0"))
        stock = int(medication.get("stock_remaining", "0"))
        daily_usage = dose_amount * len(schedules)

        if daily_usage > 0:
            days_remaining = stock // daily_usage
        else:
            days_remaining = 0

        times = ", ".join(schedule["time"] for schedule in schedules) or "No times set"

        lines.extend(
            [
                "────────────────",
                f"{medication['name']} {medication['strength']}",
                f"Dose: {medication['dose_amount']}",
                f"Times: {times}",
                f"Stock: {stock}",
                f"Estimated days remaining: {days_remaining}",
                "",
            ]
        )

    return "\n".join(lines)


async def show_medications_screen(update: Update) -> None:
    """Show medication screen."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)

    await query.edit_message_text(
        build_medication_screen(owner_id),
        reply_markup=medication_keyboard(),
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


async def cancel_add_medication(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel medication add flow."""
    query = update.callback_query
    await query.answer()

    context.user_data.pop("add_medication", None)

    await query.edit_message_text(
        "Medication setup cancelled.",
        reply_markup=medication_keyboard(),
    )


async def handle_medication_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle medication callbacks. Returns True if handled."""
    query = update.callback_query

    if query.data == "menu_medications":
        await show_medications_screen(update)
        return True

    if query.data == "med_add":
        await start_add_medication(update, context)
        return True

    if query.data == "med_cancel":
        await cancel_add_medication(update, context)
        return True

    return False


async def handle_medication_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle medication add text flow. Returns True if handled."""
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
        flow["step"] = "dose_amount"

        await update.message.reply_text(
            "How many tablets/capsules per dose?\n\nExample: 2"
        )
        return True

    if step == "dose_amount":
        if not text.isdigit():
            await update.message.reply_text("Please enter a number, for example: 2")
            return True

        data["dose_amount"] = text
        flow["step"] = "stock_remaining"

        await update.message.reply_text(
            "How many tablets/capsules do you currently have?"
        )
        return True

    if step == "stock_remaining":
        if not text.isdigit():
            await update.message.reply_text("Please enter a number, for example: 120")
            return True

        data["stock_remaining"] = text
        flow["step"] = "times"

        await update.message.reply_text(
            "What times should I remind you?\n\n"
            "Enter times separated by commas.\n\n"
            "Example: 08:00, 12:00, 16:00, 20:00"
        )
        return True

    if step == "times":
        times = [item.strip() for item in text.split(",") if item.strip()]

        if not times:
            await update.message.reply_text(
                "Please enter at least one time, for example: 08:00"
            )
            return True

        medication = add_medication(
            name=data["name"],
            strength=data["strength"],
            dose_amount=data["dose_amount"],
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

        await update.message.reply_text(
            "✅ Medication added successfully."
        )

        await update.message.reply_text(
            build_medication_screen(owner_id),
            reply_markup=medication_keyboard(),
        )

        return True

    return False