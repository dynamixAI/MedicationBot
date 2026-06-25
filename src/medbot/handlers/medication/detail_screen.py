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


def build_stock_bar(stock: int, last_refill_quantity: int, length: int = 20) -> str:
    """Build a text progress bar."""
    if last_refill_quantity <= 0:
        last_refill_quantity = max(stock, 1)

    percentage = min(stock / last_refill_quantity, 1)
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

def stock_status_message(percentage: int) -> str:
    """Return a friendly stock status message."""
    if percentage <= 20:
        return (
            "🔴 Your prescription is running low.\n\n"
            "Please arrange your next refill."
        )

    if percentage <= 50:
        return (
            "🟡 Consider ordering your next prescription soon."
        )

    return (
        "🟢 Stock level is healthy."
    )


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
    stock = int(medication.get("stock_remaining", "0"))
    last_refill_quantity = int(
        medication.get("last_refill_quantity")
        or medication.get("stock_remaining", "1")
        or "1"
    )

    daily_usage = dose_amount * len(schedules)
    days_remaining = stock // daily_usage if daily_usage > 0 else 0

    status_icon = stock_status_icon(days_remaining)
    stock_bar = build_stock_bar(stock, last_refill_quantity)

    percentage = min(round((stock / max(last_refill_quantity, 1)) * 100), 100)
    status_message = stock_status_message(percentage)

    if schedules:
        reminder_lines = "\n".join(
            f"• {schedule['time']}" for schedule in schedules
        )
    else:
        reminder_lines = "No reminder times set."

    return (
        f"💊 {medication['name']} {medication['strength']} {status_icon}\n\n"
        "Everything you need to manage this medication.\n\n"
        "💊 Dose\n"
        f"{medication['dose_amount']} tablet/capsule\n\n"
        "🕒 Reminder Times\n"
        f"{reminder_lines}\n\n"
        "📦 Current Stock\n\n"
        f"{stock_bar}\n\n"
        f"{stock} / {last_refill_quantity} tablets\n"
        f"{percentage}% remaining\n\n"
        f"{status_message}\n\n"
        "📅 Estimated Remaining\n"
        f"{days_remaining} days\n\n"
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