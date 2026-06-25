"""
menu_manager.py

Inline keyboards for MediBot screen-style navigation.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main home screen inline keyboard."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💊 My Medications", callback_data="menu_medications"),
                InlineKeyboardButton("📅 My Appointments", callback_data="menu_appointments"),
            ],
            [
                InlineKeyboardButton("📦 My Stock", callback_data="menu_stock"),
                InlineKeyboardButton("📋 My History", callback_data="menu_history"),
            ],
            [
                InlineKeyboardButton("👥 My Caregivers", callback_data="menu_caregivers"),
                InlineKeyboardButton("☰ More", callback_data="menu_more"),
            ],
        ]
    )


def back_home_keyboard() -> InlineKeyboardMarkup:
    """Back to home keyboard."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬅️ Home", callback_data="menu_home")]
        ]
    )