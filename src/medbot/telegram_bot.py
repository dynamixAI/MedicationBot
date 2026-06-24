"""
telegram_bot.py

Telegram interface for MedicationBot.
"""

import os
from medbot.message_templates import welcome_message
from medbot.profile_manager import get_display_name
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    display_name = get_display_name("default")

    await update.message.reply_text(
        welcome_message(display_name)
    )


def run_bot() -> None:
    """Start the Telegram bot."""
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing from .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))

    print("MedicationBot is running...")
    app.run_polling()