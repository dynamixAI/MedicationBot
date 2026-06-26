"""
detail_screen.py

Medication detail screen.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from medbot.medication_manager import get_medication
from medbot.schedule_manager import get_schedules_for_medication


def stock_status_icon(days_remaining: int) -> str:
    """Return stock status icon."""
    if days_remaining <= 3:
        return "🔴"

    if days_remaining <= 5:
        return "🟡"

    return "🟢"


def build_stock_bar(stock: int, starting_stock: int, length: int = 20) -> str:
    """Build a text progress bar."""
    if starting_stock <= 0:
        starting_stock = max(stock, 1)

    percentage = min(stock / starting_stock, 1)
    filled = round(percentage * length)
    empty = length - filled

    return "█" * filled + "░" * empty


def stock_status_message(percentage: int) -> str:
    """Return a friendly stock status message."""
    if percentage <= 20:
        return (
            "🔴 Your medication is running low.\n\n"
            "It may be time to arrange your next refill."
        )

    if percentage <= 50:
        return "🟡 Consider ordering your next prescription soon."

    return "🟢 Stock level is healthy."


def refill_recommendation(days_remaining: int) -> str:
    """Return calm refill guidance based on estimated days remaining."""
    if days_remaining <= 3:
        return (
            "Approximately 3 days or less remaining.\n\n"
            "It may be time to arrange your next refill."
        )

    if days_remaining <= 5:
        return (
            "Approximately 5 days or less remaining.\n\n"
            "You may want to order your prescription soon."
        )

    return "You're well stocked for now."


def plural_unit(unit: str, quantity: int) -> str:
    """Return a simple pluralised unit."""
    if quantity == 1:
        return unit

    if unit == "ml":
        return "ml"

    if unit.endswith("s"):
        return unit

    return f"{unit}s"


def medication_detail_keyboard(medication_id: str) -> InlineKeyboardMarkup:
    """Medication detail action buttons."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📦 Refill Stock",
                    callback_data=f"med_detail_refill_{medication_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "✏️ Edit Medication",
                    callback_data=f"med_edit_{medication_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "📋 Medication History",
                    callback_data=f"med_history_{medication_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Delete Medication",
                    callback_data=f"med_delete_{medication_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ My Medications",
                    callback_data="menu_medications",
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 Home",
                    callback_data="menu_home",
                )
            ],
        ]
    )


def build_medication_detail_screen(
    medication_id: str,
    owner_id: str,
) -> str:
    """Build medication detail screen."""
    medication = get_medication(medication_id, owner_id)

    if medication is None:
        return "I couldn't find that medication."

    schedules = get_schedules_for_medication(medication_id, owner_id)

    dose_amount = int(medication.get("dose_amount", "0"))
    dose_unit = medication.get("dose_unit", "unit")
    stock = int(medication.get("stock_remaining", "0"))

    starting_stock = int(
        medication.get("starting_stock")
        or medication.get("stock_remaining", "1")
        or "1"
    )

    daily_usage = dose_amount * len(schedules)
    days_remaining = stock // daily_usage if daily_usage > 0 else 0

    status_icon = stock_status_icon(days_remaining)
    stock_bar = build_stock_bar(stock, starting_stock)
    percentage = min(round((stock / max(starting_stock, 1)) * 100), 100)

    status_message = stock_status_message(percentage)
    recommendation = refill_recommendation(days_remaining)

    if schedules:
        reminder_lines = "\n".join(
            f"• {schedule['time']}" for schedule in sorted(schedules, key=lambda item: item["time"])
        )
    else:
        reminder_lines = "No reminder times set."

    schedule_count = len(schedules)
    schedule_label = "time per day" if schedule_count == 1 else "times per day"

    dose_unit_display = plural_unit(dose_unit, dose_amount)
    stock_unit_display = plural_unit(dose_unit, stock)
    starting_stock_unit_display = plural_unit(dose_unit, starting_stock)

    return (
        f"💊 {medication['name']} {medication['strength']} {status_icon}\n\n"
        "📆 Daily Schedule\n"
        f"{schedule_count} {schedule_label}\n\n"
        "💊 Dose\n"
        f"{dose_amount} {dose_unit_display}\n\n"
        "🕒 Reminder Times\n"
        f"{reminder_lines}\n\n"
        "📦 Stock Remaining\n\n"
        f"{stock_bar}\n\n"
        f"{stock} {stock_unit_display} / {starting_stock} {starting_stock_unit_display}\n"
        f"{percentage}% remaining\n\n"
        f"{status_message}\n\n"
        "📅 Estimated Remaining\n"
        f"{days_remaining} days\n\n"
        f"{recommendation}\n\n"
        "────────────────\n\n"
        "Choose an action below."
    )


async def show_medication_detail_screen(
    update: Update,
    medication_id: str,
) -> None:
    """Show medication detail screen."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)

    await query.edit_message_text(
        build_medication_detail_screen(medication_id, owner_id),
        reply_markup=medication_detail_keyboard(medication_id),
    )