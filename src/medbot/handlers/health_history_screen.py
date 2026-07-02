"""
health_history_screen.py

Global MediBot health history screen.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from medbot.activity_manager import list_activities


def health_history_keyboard() -> InlineKeyboardMarkup:
    """Health history navigation keyboard."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Home", callback_data="menu_home")]]
    )


def build_health_history_screen(owner_id: str) -> str:
    """Build global health history screen."""
    activities = list_activities(owner_id)

    screen = (
        "📊 Health History\n\n"
        "Recent Activity\n\n"
    )

    if not activities:
        return (
            screen
            + "No activity recorded yet.\n\n"
            + "As you use MediBot, your medication activity will appear here."
        )

    lines = []

    for activity in activities[:15]:
        title = activity.get("title", "Activity")
        details = activity.get("details", "")
        old_value = activity.get("old_value", "")
        new_value = activity.get("new_value", "")
        event_date = activity.get("event_date", "")
        event_time = activity.get("event_time", "")

        item = f"{title}\n{event_date} • {event_time}"

        if details:
            item += f"\n\n{details}"

        if old_value or new_value:
            item += f"\n\n{old_value} → {new_value}"

        lines.append(item)

    return screen + "\n\n────────────────\n\n".join(lines)


async def show_health_history_screen(update: Update) -> None:
    """Show global health history screen."""
    query = update.callback_query
    await query.answer()

    owner_id = str(query.from_user.id)

    await query.edit_message_text(
        build_health_history_screen(owner_id),
        reply_markup=health_history_keyboard(),
    )