"""
menu_manager.py

Telegram reply keyboards for MediBot.
"""

from telegram import ReplyKeyboardMarkup


MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["💊 My Medications", "📅 My Appointments"],
        ["📦 My Stock", "📋 My History"],
        ["👥 My Caregivers", "☰ More"],
    ],
    resize_keyboard=True,
)