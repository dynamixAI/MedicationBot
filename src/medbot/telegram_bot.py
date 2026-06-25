"""
telegram_bot.py

Telegram interface for MediBot.
"""

import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from medbot.menu_manager import MAIN_MENU
from medbot.message_templates import (
    first_time_welcome_message,
    home_dashboard_message,
    menu_placeholder_message,
    profile_created_message,
)
from medbot.profile_manager import create_or_update_profile, get_display_name


AWAITING_NAME: dict[int, bool] = {}


def get_owner_id(update: Update) -> str:
    """Use Telegram user ID as owner ID."""
    return str(update.effective_user.id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    owner_id = get_owner_id(update)
    display_name = get_display_name(owner_id)

    if display_name:
        await update.message.reply_text(
            home_dashboard_message(display_name),
            reply_markup=MAIN_MENU,
        )
        return

    AWAITING_NAME[update.effective_user.id] = True
    await update.message.reply_text(first_time_welcome_message())


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle normal text messages and menu buttons."""
    telegram_user_id = update.effective_user.id
    owner_id = get_owner_id(update)
    text = update.message.text.strip()

    if AWAITING_NAME.get(telegram_user_id):
        display_name = text.title()

        create_or_update_profile(owner_id, display_name)

        AWAITING_NAME.pop(telegram_user_id, None)

        await update.message.reply_text(
            profile_created_message(display_name),
            reply_markup=MAIN_MENU,
        )
        return

    display_name = get_display_name(owner_id) or "there"

    if text == "💊 My Medications":
        await update.message.reply_text(
            menu_placeholder_message("💊 My Medications"),
            reply_markup=MAIN_MENU,
        )
        return

    if text == "📅 My Appointments":
        await update.message.reply_text(
            menu_placeholder_message("📅 My Appointments"),
            reply_markup=MAIN_MENU,
        )
        return

    if text == "📦 My Stock":
        await update.message.reply_text(
            menu_placeholder_message("📦 My Stock"),
            reply_markup=MAIN_MENU,
        )
        return

    if text == "📋 My History":
        await update.message.reply_text(
            menu_placeholder_message("📋 My History"),
            reply_markup=MAIN_MENU,
        )
        return

    if text == "👥 My Caregivers":
        await update.message.reply_text(
            menu_placeholder_message("👥 My Caregivers"),
            reply_markup=MAIN_MENU,
        )
        return

    if text == "☰ More":
        await update.message.reply_text(
            menu_placeholder_message("☰ More"),
            reply_markup=MAIN_MENU,
        )
        return

    await update.message.reply_text(
        f"Hi {display_name}, please choose an option from the menu below.",
        reply_markup=MAIN_MENU,
    )


def run_bot() -> None:
    """Start the Telegram bot."""
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing from .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("MediBot is running...")
    app.run_polling()