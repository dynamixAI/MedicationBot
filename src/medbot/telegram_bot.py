"""
telegram_bot.py

Telegram interface for MediBot.
"""

import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from medbot.handlers.home_handler import handle_main_menu_callback
from medbot.menu_manager import main_menu_keyboard
from medbot.message_templates import (
    first_time_welcome_message,
    home_dashboard_message,
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

    display_name = get_display_name(owner_id) or "there"

    await update.message.reply_text(
        f"Hi {display_name}, please use the menu below.",
        reply_markup=main_menu_keyboard(),
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all inline button callbacks."""
    await handle_main_menu_callback(update)


def run_bot() -> None:
    """Start the Telegram bot."""
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing from .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("MediBot is running...")
    app.run_polling()