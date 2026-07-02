"""
home_handler.py

Handles MediBot home screen and main menu callbacks.
"""

from telegram import Update

from medbot.handlers.health_history_screen import show_health_history_screen
from medbot.menu_manager import back_home_keyboard, main_menu_keyboard
from medbot.message_templates import home_dashboard_message, menu_placeholder_message
from medbot.profile_manager import get_display_name


def get_owner_id_from_query(update: Update) -> str:
    """Use Telegram user ID from callback query as owner ID."""
    return str(update.callback_query.from_user.id)


async def show_home_from_query(update: Update) -> None:
    """Show home dashboard after a button tap."""
    query = update.callback_query
    await query.answer()

    owner_id = get_owner_id_from_query(update)
    display_name = get_display_name(owner_id) or "there"

    await query.edit_message_text(
        home_dashboard_message(display_name),
        reply_markup=main_menu_keyboard(),
    )


async def show_placeholder_screen(update: Update, title: str) -> None:
    """Show placeholder screen."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        menu_placeholder_message(title),
        reply_markup=back_home_keyboard(),
    )


async def handle_main_menu_callback(update: Update) -> None:
    """Route main menu callback data."""
    query = update.callback_query
    data = query.data

    if data == "menu_home":
        await show_home_from_query(update)
        return

    if data == "menu_health_history":
        await show_health_history_screen(update)
        return

    screens = {
        "menu_appointments": "📅 My Appointments",
        "menu_caregivers": "👥 My Caregivers",
        "menu_more": "☰ More",
        "menu_settings": "⚙️ Settings",
    }

    title = screens.get(data)

    if title:
        await show_placeholder_screen(update, title)