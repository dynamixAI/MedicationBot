"""
telegram_bot.py

Telegram interface for MediBot.
"""

import asyncio
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from medbot.reminder_state_manager import mark_dose_confirmed, mark_dose_snoozed

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from medbot.handlers.home_handler import handle_main_menu_callback
from medbot.handlers.medication_handler import (
    handle_medication_callback,
    handle_medication_text,
)
from medbot.inventory_manager import reduce_stock
from medbot.menu_manager import main_menu_keyboard
from medbot.message_templates import (
    first_time_welcome_message,
    home_dashboard_message,
    profile_created_message,
)
from medbot.profile_manager import create_or_update_profile, get_display_name
from medbot.reminder_engine import get_due_reminders
from medbot.reminder_state_manager import mark_dose_confirmed


AWAITING_NAME: dict[int, bool] = {}


def get_owner_id(update: Update) -> str:
    """Use Telegram user ID as owner ID."""
    return str(update.effective_user.id)


def reminder_keyboard(dose_id: str) -> InlineKeyboardMarkup:
    """Reminder confirmation keyboard."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Taken", callback_data=f"dose_taken|{dose_id}")],
            [InlineKeyboardButton("⏰ Snooze 15 mins", callback_data=f"dose_snooze|{dose_id}")],
            [InlineKeyboardButton("❌ Skip", callback_data=f"dose_skip|{dose_id}")],
        ]
    )


def build_reminder_message(reminder: dict[str, str]) -> str:
    """Build reminder message."""
    medication = f"{reminder['medication_name']} {reminder['strength']}"
    dose = f"{reminder['dose_amount']} {reminder['dose_unit']}"

    if reminder["reminder_type"] == "pre":
        return (
            "🔔 Upcoming Medication\n\n"
            "In 15 minutes, it's time to take:\n\n"
            f"💊 {medication}\n\n"
            f"Dose:\n{dose}\n\n"
            f"Scheduled for {reminder['scheduled_time']}."
        )

    if reminder["reminder_type"] == "due":
        return (
            "🔔 Medication Reminder\n\n"
            "It's time to take:\n\n"
            f"💊 {medication}\n\n"
            f"Dose:\n{dose}\n\n"
            "Please confirm once taken."
        )
    
    if reminder["reminder_type"] == "repeat":
        return (
            "⏰ Medication Reminder\n\n"
            "I haven't received confirmation yet.\n\n"
            f"Medication:\n💊 {medication}\n\n"
            f"Dose:\n{dose}\n\n"
            f"Scheduled for {reminder['scheduled_time']}.\n\n"
            "Please confirm once taken."
        )




    if reminder["reminder_type"] == "thirty":
        return (
            "⏰ Medication Reminder\n\n"
            "I haven't received confirmation yet.\n\n"
            f"Medication:\n💊 {medication}\n\n"
            f"Scheduled for {reminder['scheduled_time']}.\n\n"
            "Please confirm if you've taken it."
        )

    if reminder["reminder_type"] == "sixty":
        return (
            "⚠️ Final Medication Reminder\n\n"
            "I still haven't received confirmation for:\n\n"
            f"💊 {medication}\n\n"
            f"Scheduled for {reminder['scheduled_time']}.\n\n"
            "If you've already taken it, please tap ✅ Taken."
        )

    return "Medication reminder."


async def reminder_loop(app: Application) -> None:
    """Check and send reminders every minute using UK local time."""
    last_checked_minute = None

    while True:
        now = datetime.now(ZoneInfo("Europe/London")).replace(
            second=0,
            microsecond=0,
            tzinfo=None,
        )

        if now != last_checked_minute:
            last_checked_minute = now
            reminders = get_due_reminders(now)
            print(f"[{now.strftime('%H:%M')}] Found {len(reminders)} reminder(s)")

            for reminder in reminders:
                await app.bot.send_message(
                    chat_id=int(reminder["owner_id"]),
                    text=build_reminder_message(reminder),
                    reply_markup=reminder_keyboard(reminder["dose_id"]),
                )

        await asyncio.sleep(10)


async def post_init(app: Application) -> None:
    """Start background reminder loop."""
    asyncio.create_task(reminder_loop(app))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    owner_id = get_owner_id(update)
    display_name = get_display_name(owner_id)

    if display_name:
        await update.message.reply_text(
            home_dashboard_message(display_name),
            reply_markup=main_menu_keyboard(),
        )
        return

    AWAITING_NAME[update.effective_user.id] = True
    await update.message.reply_text(first_time_welcome_message())


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle normal text messages."""
    telegram_user_id = update.effective_user.id
    owner_id = get_owner_id(update)
    text = update.message.text.strip()

    if AWAITING_NAME.get(telegram_user_id):
        display_name = text.title()
        create_or_update_profile(owner_id, display_name)
        AWAITING_NAME.pop(telegram_user_id, None)

        await update.message.reply_text(
            profile_created_message(display_name),
            reply_markup=main_menu_keyboard(),
        )
        return

    if await handle_medication_text(update, context):
        return

    display_name = get_display_name(owner_id) or "there"

    await update.message.reply_text(
        f"Hi {display_name}, please use the menu below.",
        reply_markup=main_menu_keyboard(),
    )


async def handle_dose_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """Handle dose confirmation callbacks."""
    query = update.callback_query
    data = query.data

    if data.startswith("dose_taken|"):
        dose_id = data.replace("dose_taken|", "")
        parts = dose_id.split("_")

        if len(parts) >= 4:
            owner_id = parts[0]
            medication_id = parts[1]

            reduce_stock(
                medication_id=medication_id,
                quantity_taken="1",
                owner_id=owner_id,
            )

        mark_dose_confirmed(dose_id, "taken")

        await query.answer()
        await query.edit_message_text(
            "✅ Dose recorded\n\n"
            "Great! I've updated your medication record and stock remaining.\n\n"
            "See you at your next reminder.",
            reply_markup=main_menu_keyboard(),
        )
        return True

    if data.startswith("dose_skip|"):
        dose_id = data.replace("dose_skip|", "")

        mark_dose_confirmed(dose_id, "skipped")

        await query.answer()
        await query.edit_message_text(
            "Dose skipped.\n\n"
            "No further reminders will be sent for this scheduled dose.",
            reply_markup=main_menu_keyboard(),
        )
        return True

    if data.startswith("dose_snooze|"):
        dose_id = data.replace("dose_snooze|", "")

        snoozed_until = (
            datetime.now(ZoneInfo("Europe/London")) + timedelta(minutes=15)
        ).strftime("%H:%M")

        mark_dose_snoozed(dose_id, snoozed_until)

        await query.answer()
        await query.edit_message_text(
            "Okay 👍\n\n"
            f"I'll remind you again at {snoozed_until}.",
            reply_markup=main_menu_keyboard(),
        )
        return True

    return False


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all inline button callbacks."""
    if await handle_dose_callback(update, context):
        return

    if await handle_medication_callback(update, context):
        return

    await handle_main_menu_callback(update)


def run_bot() -> None:
    """Start the Telegram bot."""
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing from .env")

    app = Application.builder().token(token).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("MediBot is running...")
    app.run_polling()